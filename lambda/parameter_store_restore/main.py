import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

ssm = boto3.client('ssm')
s3 = boto3.client('s3')

def download_backup(bucket, key):
    try:
        resp = s3.get_object(Bucket=bucket, Key=key)
        return resp['Body'].read().decode('utf-8')
    except ClientError as e:
        LOG.error('Failed to download s3://%s/%s: %s', bucket, key, e)
        return None


def find_most_recent_backup(bucket, prefix='ssm-backup-'):
    """Return the key of the most recent object in `bucket` whose key starts with `prefix`.
    Returns None if no matching objects are found.
    """
    try:
        paginator = s3.get_paginator('list_objects_v2')
        most_recent = None
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get('Contents', []) or []:
                if most_recent is None or obj['LastModified'] > most_recent['LastModified']:
                    most_recent = obj
        if most_recent:
            return most_recent['Key']
        return None
    except ClientError as e:
        LOG.error('Failed to list objects in s3://%s with prefix %s: %s', bucket, prefix, e)
        return None

def put_parameter(name, value, type_):
    try:
        kwargs = {
            'Name': name,
            'Value': value,
            'Type': type_,
            'Overwrite': True
        }
        if type_ == 'SecureString':
            # Let KMS default key decrypt/encrypt; to use custom KMS key add KeyId
            pass
        ssm.put_parameter(**kwargs)
        return True
    except ClientError as e:
        LOG.error('Failed to put parameter %s: %s', name, e)
        return False

def handler(event, context):
    """Restore parameters from an S3 backup. Provide bucket/key in env or event.

    Event example:
    {"bucket": "my-bucket", "key": "ssm-backup-...json"}
    """
    bucket = os.environ.get('BUCKET')
    key = None
    if isinstance(event, dict):
        # Accept multiple key names for convenience
        key = event.get('key') or event.get('Key') or event.get('s3_key')
        bucket = event.get('bucket') or bucket

    if not bucket:
        LOG.error('Missing bucket (env BUCKET not set and no bucket in event)')
        return {'statusCode': 400, 'body': 'Missing bucket'}

    # If key not provided, try to find the most recent backup in the bucket
    if not key:
        LOG.info('No key provided, looking up the latest backup in s3://%s', bucket)
        key = find_most_recent_backup(bucket)
        if key:
            LOG.info('Using latest backup key: %s', key)
        else:
            LOG.error('No backups found in bucket %s', bucket)
            return {'statusCode': 400, 'body': 'No backup key provided and no backups found in bucket'}

    data = download_backup(bucket, key)
    if data is None:
        return {'statusCode': 500, 'body': 'Failed to download backup'}

    try:
        items = json.loads(data)
    except Exception as e:
        LOG.error('Invalid JSON in backup: %s', e)
        return {'statusCode': 400, 'body': 'Invalid JSON'}

    restored = 0
    for item in items:
        name = item.get('Name')
        value = item.get('Value')
        type_ = item.get('Type') or 'String'
        if put_parameter(name, value, type_):
            restored += 1

    LOG.info('Restored %d parameters to SSM from s3://%s/%s', restored, bucket, key)
    return {'statusCode': 200, 'body': json.dumps({'restored': restored})}

import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

ssm = boto3.client('ssm')
s3 = boto3.client('s3')

def list_all_parameters():
    paginator = ssm.get_paginator('describe_parameters')
    for page in paginator.paginate():
        for p in page.get('Parameters', []):
            yield p

def get_parameter_value(name):
    try:
        resp = ssm.get_parameter(Name=name, WithDecryption=True)
        return resp.get('Parameter', {}).get('Value')
    except ClientError as e:
        LOG.error('Failed to get parameter %s: %s', name, e)
        return None

def handler(event, context):
    """Backup all SSM Parameter Store parameters into a JSON file and upload to S3."""
    bucket = os.environ.get('BUCKET')
    if not bucket:
        LOG.error('BUCKET environment variable not set')
        return {'statusCode': 500, 'body': 'No BUCKET env var'}

    backup = []
    for p in list_all_parameters():
        name = p.get('Name')
        value = get_parameter_value(name)
        if value is None:
            continue
        backup.append({
            'Name': name,
            'Type': p.get('Type'),
            'Value': value,
            'Version': p.get('Version')
        })

    key = f'ssm-backup-{context.aws_request_id}.json'
    body = json.dumps(backup)

    try:
        s3.put_object(Bucket=bucket, Key=key, Body=body.encode('utf-8'))
    except ClientError as e:
        LOG.error('Failed to upload backup to s3://%s/%s: %s', bucket, key, e)
        return {'statusCode': 500, 'body': 'Failed to upload to S3'}

    LOG.info('Uploaded backup to s3://%s/%s (items=%d)', bucket, key, len(backup))
    return {'statusCode': 200, 'body': json.dumps({'bucket': bucket, 'key': key, 'count': len(backup)})}

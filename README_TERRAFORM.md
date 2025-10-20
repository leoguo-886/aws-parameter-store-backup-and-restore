# Terraform Lambda deployment

This folder contains Terraform configuration to deploy two simple AWS Lambda functions.

Prerequisites
- Terraform 1.0+
- AWS credentials configured in your environment (e.g. AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN optional). The provider will use standard environment variables or shared config.

Quick start

1. Initialize Terraform

```bash
terraform init
```

2. Preview

```bash
terraform plan -out plan.tfplan
```

3. Apply

```bash
terraform apply "plan.tfplan"
```

Notes
- The build artifacts (zip files) will be placed into `./build`.
 - Handlers are in `lambda/parameter_store_backup` and `lambda/parameter_store_restore`.

Changing region

You can change the deployment region by setting the `aws_region` variable. Either edit `variables.tf` or pass `-var 'aws_region=us-west-2'` to `terraform plan`/`apply`.

Cleaning up

Run `terraform destroy` to remove the created resources when you're done.

Backup & restore details

- `function_one` (named `tf-ps-backup`) will enumerate all SSM Parameter Store parameters and store a JSON backup into the S3 bucket created by Terraform. The backup file key will be `ssm-backup-<request-id>.json`.
 - `parameter_store_backup` (named `parameter_store_backup`) will enumerate all SSM Parameter Store parameters and store a JSON backup into the S3 bucket created by Terraform. The backup file key will be `ssm-backup-<request-id>.json`.
 - `parameter_store_restore` (named `parameter_store_restore`) restores parameters from a specified S3 object. Provide `{ "bucket": "...", "key": "ssm-backup-...json" }` as the event body if invoking manually.
- An EventBridge rule triggers the backup lambda every Friday at 8 PM Sydney time.

Permissions

- The lambdas have an inline policy that allows SSM read/write operations, S3 Put/Get, and KMS encrypt/decrypt operations. Review and narrow these permissions to least privilege before using in production.

# AWS Parameter Store Backup and Restore

This repository provides:

- Terraform to deploy two Lambda functions that back up and restore AWS SSM Parameter Store to S3.
- Lambda source code under `lambda/parameter_store_backup` and `lambda/parameter_store_restore`.

Structure

- `terraform/` — Terraform configuration (provider, resources, outputs). Run Terraform from this directory.
- `lambda/` — Lambda function source folders and helpers.
- `build/` — Build artifacts (zips created by Terraform's `archive_file` data source).

Quick start

```bash
cd terraform
terraform init
terraform validate
terraform plan -out plan.tfplan
terraform apply "plan.tfplan"
```

Notes

- The lambdas use the AWS-provided `boto3` library — no vendor packaging required unless you add extra dependencies.
- Backups are stored in an S3 bucket named `parameter-store-backup-<random>` created by Terraform.

If you want, I can add automation to build zip artifacts and run `terraform apply` with one command.
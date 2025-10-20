# Terraform for parameter store backup & restore

This folder contains the Terraform configuration for deploying two Lambda functions that back up and restore SSM Parameter Store to S3.

Quick start

```bash
cd terraform
terraform init
terraform validate
terraform plan -out plan.tfplan
terraform apply "plan.tfplan"
```

Notes
- The lambda source code is in `../lambda/parameter_store_backup` and `../lambda/parameter_store_restore`.
- Build artifacts (zip files) are written to `../build` by the `archive_file` data source.
- Adjust `variables.tf` to change the region.

Cleaning up

```bash
terraform destroy
```

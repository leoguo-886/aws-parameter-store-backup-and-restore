output "parameter_store_backup_name" {
  value = aws_lambda_function.parameter_store_backup.function_name
}

output "parameter_store_restore_name" {
  value = aws_lambda_function.parameter_store_restore.function_name
}

output "backups_bucket" {
  value = aws_s3_bucket.ssm_backups.bucket
}

resource "aws_lambda_function" "parameter_store_backup" {
  function_name = "parameter_store_backup"
  filename      = data.archive_file.parameter_store_backup_zip.output_path
  source_code_hash = data.archive_file.parameter_store_backup_zip.output_base64sha256
  handler       = "main.handler"
  runtime       = "python3.10"
  role          = aws_iam_role.lambda_role.arn
  depends_on    = [aws_iam_role_policy_attachment.lambda_basic_execution, aws_iam_role_policy.lambda_ssm_s3_policy]

  environment {
    variables = {
      BUCKET = aws_s3_bucket.ssm_backups.bucket
    }
  }
}

resource "aws_lambda_function" "parameter_store_restore" {
  function_name = "parameter_store_restore"
  filename      = data.archive_file.parameter_store_restore_zip.output_path
  source_code_hash = data.archive_file.parameter_store_restore_zip.output_base64sha256
  handler       = "main.handler"
  runtime       = "python3.10"
  role          = aws_iam_role.lambda_role.arn
  depends_on    = [aws_iam_role_policy_attachment.lambda_basic_execution, aws_iam_role_policy.lambda_ssm_s3_policy]

  environment {
    variables = {
      BUCKET = aws_s3_bucket.ssm_backups.bucket
    }
  }
}

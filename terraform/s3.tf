resource "aws_s3_bucket" "ssm_backups" {
  bucket = "parameter-store-backup-${random_id.bucket_id.hex}"
}

# Enable versioning using the separate resource (newer provider syntax)
resource "aws_s3_bucket_versioning" "ssm_backups" {
  bucket = aws_s3_bucket.ssm_backups.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption configuration (SSE-S3) as separate resource
resource "aws_s3_bucket_server_side_encryption_configuration" "ssm_backups" {
  bucket = aws_s3_bucket.ssm_backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lifecycle configuration as separate resource
resource "aws_s3_bucket_lifecycle_configuration" "ssm_backups" {
  bucket = aws_s3_bucket.ssm_backups.id

  rule {
    id     = "cleanup-old-backups"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

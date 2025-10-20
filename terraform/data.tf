data "archive_file" "parameter_store_backup_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/parameter_store_backup"
  output_path = "${path.module}/../build/parameter_store_backup.zip"
}

data "archive_file" "parameter_store_restore_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/parameter_store_restore"
  output_path = "${path.module}/../build/parameter_store_restore.zip"
}

resource "random_id" "bucket_id" {
  byte_length = 4
}

// Use EventBridge Scheduler to run the backup on a weekly schedule
resource "aws_iam_role" "scheduler_invoke_role" {
  name = "tf_scheduler_invoke_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "scheduler.amazonaws.com" },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "scheduler_invoke_policy" {
  name = "scheduler-invoke-lambda"
  role = aws_iam_role.scheduler_invoke_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["lambda:InvokeFunction"],
        Resource = [aws_lambda_function.parameter_store_backup.arn]
      }
    ]
  })
}

resource "aws_scheduler_schedule" "weekly_backup" {
  name                        = "parameter-store-weekly-backup"
  schedule_expression         = "cron(0 20 ? * FRI *)"
  schedule_expression_timezone = "Australia/Sydney"
  description                 = "Trigger Parameter Store backup every Friday at 20:00 Australia/Sydney"

  target {
    arn      = aws_lambda_function.parameter_store_backup.arn
    role_arn = aws_iam_role.scheduler_invoke_role.arn
    input    = jsonencode({})
  }

  flexible_time_window {
    mode = "FLEXIBLE"
    maximum_window_in_minutes = 60
  }
}

output "log_group_name" {
  value       = aws_cloudwatch_log_group.hawkgrid_logs.name
  description = "The name of the log group where HawkGrid reads telemetry"
}

output "forensic_bucket" {
  value = aws_s3_bucket.trail_logs.id
}
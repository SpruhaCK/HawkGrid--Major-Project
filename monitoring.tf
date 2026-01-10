# NEW: Get the current AWS Account ID dynamically
data "aws_caller_identity" "current" {}

# 1. CloudWatch Log Group for Network Telemetry
resource "aws_cloudwatch_log_group" "hawkgrid_logs" {
  name              = "/aws/hawkgrid/network-telemetry"
  retention_in_days = 7
}

# 2. VPC Flow Logs
resource "aws_flow_log" "hawkgrid_flow_log" {
  iam_role_arn    = aws_iam_role.flow_log_role.arn
  log_destination = aws_cloudwatch_log_group.hawkgrid_logs.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}

# 3. S3 Bucket for Forensic Logs
resource "aws_s3_bucket" "trail_logs" {
  bucket        = "hawkgrid-forensic-logs-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

# 4. NEW: S3 Bucket Policy (This fixes your error)
resource "aws_s3_bucket_policy" "trail_bucket_policy" {
  bucket = aws_s3_bucket.trail_logs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.trail_logs.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.trail_logs.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"
        Condition = {
          StringEquals = { "s3:x-amz-acl" = "bucket-owner-full-control" }
        }
      }
    ]
  })
}

# 5. CloudTrail
resource "aws_cloudtrail" "hawkgrid_trail" {
  name                          = "hawkgrid-activity-monitor"
  s3_bucket_name                = aws_s3_bucket.trail_logs.id
  include_global_service_events = true
  
  # Ensure the policy is created BEFORE the trail tries to use the bucket
  depends_on = [aws_s3_bucket_policy.trail_bucket_policy]
}
output "public_ip" {
  value = aws_instance.app.public_ip
}

output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_apigatewayv2_api.api.api_endpoint}/scrape"
}

output "s3_bucket" {
  description = "S3 bucket for storing reports"
  value       = aws_s3_bucket.reports.id
}

output "dynamodb_table" {
  description = "DynamoDB table for job status"
  value       = aws_dynamodb_table.job_status.name
}

output "sqs_queues" {
  description = "SQS queue URLs"
  value = {
    scraper = aws_sqs_queue.scraper_queue.url
    email   = aws_sqs_queue.email_queue.url
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_key_pair" "deployer" {
  key_name   = var.key_name
  public_key = file(var.public_key_path)
}

# VPC and networking
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.project_name}-public-subnet"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "${var.project_name}-igw"
  }
}

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  
  tags = {
    Name = "${var.project_name}-rt"
  }
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.rt.id
}

resource "aws_security_group" "app_sg" {
  name        = "${var.project_name}-sg"
  description = "Allow SSH and app traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "RabbitMQ UI"
    from_port   = 15672
    to_port     = 15672
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.project_name}-sg"
  }
}

# EC2 instance with cost optimization
resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.public.id
  key_name      = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  # Cost optimization features
  instance_market_options {
    market_type = "spot"
    spot_options {
      max_price = "0.0172" # Maximum price per hour (adjust based on your needs)
      spot_instance_type = "persistent"
    }
  }

  lifecycle {
    create_before_destroy = true
  }

  # EBS optimization for better performance
  ebs_optimized = true

  # Root volume configuration
  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    delete_on_termination = true
    
    tags = {
      Name = "${var.project_name}-root-volume"
    }
  }

  # User data script for initialization
  user_data = file("init.sh")

  tags = {
    Name = "${var.project_name}-instance"
  }
}

# CloudWatch alarm for cost monitoring
resource "aws_cloudwatch_metric_alarm" "cpu_utilization" {
  alarm_name          = "${var.project_name}-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period             = "300"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "This metric monitors EC2 CPU utilization"
  alarm_actions      = [] # Add SNS topic ARN if you want notifications
  
  dimensions = {
    InstanceId = aws_instance.app.id
  }
}

# SQS Queues
resource "aws_sqs_queue" "scraper_queue" {
  name                      = "${var.project_name}-scraper-queue"
  message_retention_seconds = 86400  # 1 day
  visibility_timeout_seconds = 300   # 5 minutes
  delay_seconds             = 0
  receive_wait_time_seconds = 0

  tags = {
    Name = "${var.project_name}-scraper-queue"
  }
}

resource "aws_sqs_queue" "email_queue" {
  name                      = "${var.project_name}-email-queue"
  message_retention_seconds = 86400  # 1 day
  visibility_timeout_seconds = 30    # 30 seconds
  delay_seconds             = 0
  receive_wait_time_seconds = 0

  tags = {
    Name = "${var.project_name}-email-queue"
  }
}

# DynamoDB table for job status
resource "aws_dynamodb_table" "job_status" {
  name           = "${var.project_name}-job-status"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "job_id"
  range_key      = "timestamp"

  attribute {
    name = "job_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-job-status"
  }
}

# S3 bucket for reports
resource "aws_s3_bucket" "reports" {
  bucket = "${var.project_name}-reports-${var.environment}"
  
  tags = {
    Name = "${var.project_name}-reports"
  }
}

resource "aws_s3_bucket_versioning" "reports" {
  bucket = aws_s3_bucket.reports.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id

  rule {
    id     = "delete-old-reports"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = 30
    }
  }
}

# ElastiCache for Redis
resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project_name}-redis-subnet"
  subnet_ids = [aws_subnet.public.id]  # Using public subnet since we removed private
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.project_name}-redis"
  engine              = "redis"
  node_type           = "cache.t4g.micro"  # Smallest instance type
  num_cache_nodes     = 1
  parameter_group_name = "default.redis7"
  subnet_group_name   = aws_elasticache_subnet_group.redis.name
  security_group_ids  = [aws_security_group.redis.id]
}

# Lambda Layer for Chrome
resource "aws_lambda_layer_version" "chrome" {
  filename         = "lambda/chrome_layer.zip"
  layer_name       = "${var.project_name}-chrome"
  description      = "Chrome binary for scraper worker"
  compatible_runtimes = ["python3.9"]
}

# Lambda Layer for dependencies
resource "aws_lambda_layer_version" "scraper_deps" {
  filename         = "lambda/scraper_worker/layer.zip"
  layer_name       = "${var.project_name}-scraper-deps"
  description      = "Dependencies for scraper worker"
  compatible_runtimes = ["python3.9"]
}

resource "aws_lambda_layer_version" "email_deps" {
  filename         = "lambda/email_worker/layer.zip"
  layer_name       = "${var.project_name}-email-deps"
  description      = "Dependencies for email worker"
  compatible_runtimes = ["python3.9"]
}

# Lambda Functions
resource "aws_lambda_function" "scraper_worker" {
  filename         = "lambda/scraper_worker/function.zip"
  function_name    = "${var.project_name}-scraper-worker"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300  # 5 minutes
  memory_size     = 1024

  environment {
    variables = {
      SQS_EMAIL_QUEUE_URL = aws_sqs_queue.email_queue.url
      DYNAMODB_TABLE     = aws_dynamodb_table.job_status.name
      S3_BUCKET          = aws_s3_bucket.reports.id
    }
  }

  layers = [
    aws_lambda_layer_version.chrome.arn,
    aws_lambda_layer_version.scraper_deps.arn
  ]

  vpc_config {
    subnet_ids         = [aws_subnet.public.id]
    security_group_ids = [aws_security_group.lambda.id]
  }

  tags = {
    Name = "${var.project_name}-scraper-worker"
  }
}

resource "aws_lambda_function" "email_worker" {
  filename         = "lambda/email_worker/function.zip"
  function_name    = "${var.project_name}-email-worker"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.job_status.name
      S3_BUCKET      = aws_s3_bucket.reports.id
    }
  }

  layers = [aws_lambda_layer_version.email_deps.arn]

  tags = {
    Name = "${var.project_name}-email-worker"
  }
}

# Lambda Event Source Mappings
resource "aws_lambda_event_source_mapping" "scraper_queue" {
  event_source_arn = aws_sqs_queue.scraper_queue.arn
  function_name    = aws_lambda_function.scraper_worker.function_name
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "email_queue" {
  event_source_arn = aws_sqs_queue.email_queue.arn
  function_name    = aws_lambda_function.email_worker.function_name
  batch_size       = 1
}

# API Gateway
resource "aws_apigatewayv2_api" "api" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "api" {
  api_id = aws_apigatewayv2_api.api.id
  name   = "prod"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "api" {
  api_id           = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"

  integration_uri    = aws_lambda_function.scraper_worker.invoke_arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "api" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /scrape"
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

# IAM roles and policies
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_s3" {
  name = "${var.project_name}-lambda-s3"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.reports.arn,
          "${aws_s3_bucket.reports.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_sqs" {
  name = "${var.project_name}-lambda-sqs"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [
          aws_sqs_queue.scraper_queue.arn,
          aws_sqs_queue.email_queue.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "${var.project_name}-lambda-dynamodb"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.job_status.arn
      }
    ]
  })
}

# Security groups
resource "aws_security_group" "redis" {
  name        = "${var.project_name}-redis"
  description = "Redis security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }
}

resource "aws_security_group" "lambda" {
  name        = "${var.project_name}-lambda"
  description = "Lambda security group"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

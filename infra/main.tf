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
    }
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

# S3 bucket for reports backup
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

# Lifecycle rule to delete old reports
resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id

  rule {
    id     = "delete-old-reports"
    status = "Enabled"

    expiration {
      days = 30 # Keep reports for 30 days
    }
  }
}

# ElastiCache for Redis
resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project_name}-redis-subnet"
  subnet_ids = [aws_subnet.private.id]
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

# Amazon MQ for RabbitMQ
resource "aws_mq_broker" "rabbitmq" {
  broker_name = "${var.project_name}-rabbitmq"

  engine_type        = "RabbitMQ"
  engine_version     = "3.10.20"
  host_instance_type = "mq.t3.micro"  # Smallest instance type
  security_groups    = [aws_security_group.rabbitmq.id]
  subnet_ids         = [aws_subnet.private.id]

  user {
    username = var.rabbitmq_username
    password = var.rabbitmq_password
  }
}

# Lambda functions
resource "aws_lambda_function" "api" {
  filename         = "../src/api/lambda_function.zip"
  function_name    = "${var.project_name}-api"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      REDIS_URL        = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:6379"
      RABBITMQ_URL     = "amqp://${var.rabbitmq_username}:${var.rabbitmq_password}@${aws_mq_broker.rabbitmq.instances[0].endpoints[0]}:5672"
      S3_BUCKET        = aws_s3_bucket.reports.id
    }
  }
}

resource "aws_lambda_function" "scraper_worker" {
  filename         = "../src/workers/scraper_worker/lambda_function.zip"
  function_name    = "${var.project_name}-scraper-worker"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300  # 5 minutes
  memory_size     = 512

  environment {
    variables = {
      REDIS_URL        = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:6379"
      RABBITMQ_URL     = "amqp://${var.rabbitmq_username}:${var.rabbitmq_password}@${aws_mq_broker.rabbitmq.instances[0].endpoints[0]}:5672"
      S3_BUCKET        = aws_s3_bucket.reports.id
    }
  }
}

resource "aws_lambda_function" "email_worker" {
  filename         = "../src/workers/email_worker/lambda_function.zip"
  function_name    = "${var.project_name}-email-worker"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      REDIS_URL        = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:6379"
      RABBITMQ_URL     = "amqp://${var.rabbitmq_username}:${var.rabbitmq_password}@${aws_mq_broker.rabbitmq.instances[0].endpoints[0]}:5672"
      S3_BUCKET        = aws_s3_bucket.reports.id
      GOOGLE_APP_PW    = var.google_app_pw
      GOOGLE_SENDER_EMAIL = var.google_sender_email
    }
  }
}

# API Gateway
resource "aws_apigatewayv2_api" "api" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "api" {
  api_id = aws_apigatewayv2_api.api.id
  name   = var.environment
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "api" {
  api_id           = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"

  connection_type    = "INTERNET"
  description        = "Lambda integration"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.api.invoke_arn
}

resource "aws_apigatewayv2_route" "api" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

# IAM role for Lambda
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
          "s3:GetObject",
          "s3:PutObject",
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

# VPC and networking
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
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

resource "aws_security_group" "rabbitmq" {
  name        = "${var.project_name}-rabbitmq"
  description = "RabbitMQ security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5672
    to_port     = 5672
    protocol    = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }

  ingress {
    from_port   = 15672
    to_port     = 15672
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

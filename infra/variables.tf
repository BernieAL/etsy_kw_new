variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "etsy-keyword-analyzer"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "rabbitmq_username" {
  description = "Username for RabbitMQ"
  type        = string
  sensitive   = true
}

variable "rabbitmq_password" {
  description = "Password for RabbitMQ"
  type        = string
  sensitive   = true
}

variable "google_app_pw" {
  description = "Google App Password for email sending"
  type        = string
  sensitive   = true
}

variable "google_sender_email" {
  description = "Google email address for sending emails"
  type        = string
}

variable "instance_type" {
  default = "t2.micro"
}

variable "ami_id" {
  description = "Ubuntu 22.04 LTS"
  default     = "ami-053b0d53c279acc90" # check region!
}

variable "key_name" {}
variable "public_key_path" {}

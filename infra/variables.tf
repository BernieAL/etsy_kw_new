variable "aws_region" {
  default = "us-east-1"
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

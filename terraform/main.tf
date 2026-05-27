terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for storing uploaded resumes
resource "aws_s3_bucket" "resumeiq_uploads" {
  bucket = "${var.project_name}-uploads-${var.environment}"

  tags = {
    Name        = "${var.project_name}-uploads"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "resumeiq_uploads" {
  bucket = aws_s3_bucket.resumeiq_uploads.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "resumeiq_uploads" {
  bucket = aws_s3_bucket.resumeiq_uploads.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Security group for backend EC2 instance
resource "aws_security_group" "resumeiq_backend" {
  name        = "${var.project_name}-backend-sg"
  description = "Security group for ResumeIQ Flask backend"

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
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
    Name    = "${var.project_name}-backend-sg"
    Project = var.project_name
  }
}

# EC2 instance for Flask backend
resource "aws_instance" "resumeiq_backend" {
  ami           = var.ami_id
  instance_type = "t3.micro"

  vpc_security_group_ids = [aws_security_group.resumeiq_backend.id]

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
  EOF

  tags = {
    Name        = "${var.project_name}-backend"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Elastic IP for stable endpoint
resource "aws_eip" "resumeiq_backend" {
  instance = aws_instance.resumeiq_backend.id
  domain   = "vpc"

  tags = {
    Name    = "${var.project_name}-eip"
    Project = var.project_name
  }
}

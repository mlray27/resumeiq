output "backend_public_ip" {
  description = "Public IP of the Flask backend EC2 instance"
  value       = aws_eip.resumeiq_backend.public_ip
}

output "s3_bucket_name" {
  description = "S3 bucket name for resume uploads"
  value       = aws_s3_bucket.resumeiq_uploads.bucket
}

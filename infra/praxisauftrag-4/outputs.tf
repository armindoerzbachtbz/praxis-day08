output "public_ip" {
  description = "Public IP address of the EC2 instance."
  value       = aws_instance.techstyle.public_ip
}

output "public_dns" {
  description = "Public DNS name of the EC2 instance."
  value       = aws_instance.techstyle.public_dns
}

output "app_url" {
  description = "URL of the TechStyle app after deployment."
  value       = "http://${aws_instance.techstyle.public_dns}:5001"
}

output "ssh_command" {
  description = "SSH command for connecting to the EC2 instance."
  value       = "ssh ubuntu@${aws_instance.techstyle.public_dns}"
}

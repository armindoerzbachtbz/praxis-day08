output "blue_public_ip" {
  description = "Public IPv4 address of the blue EC2 instance."
  value       = aws_instance.app["blue"].public_ip
}

output "green_public_ip" {
  description = "Public IPv4 address of the green EC2 instance."
  value       = aws_instance.app["green"].public_ip
}

output "blue_public_dns" {
  description = "Public DNS name of the blue EC2 instance."
  value       = aws_instance.app["blue"].public_dns
}

output "green_public_dns" {
  description = "Public DNS name of the green EC2 instance."
  value       = aws_instance.app["green"].public_dns
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer."
  value       = aws_lb.app.dns_name
}

output "alb_url" {
  description = "Public URL of the Application Load Balancer."
  value       = "http://${aws_lb.app.dns_name}"
}

output "alb_listener_arn" {
  description = "ARN of the ALB HTTP listener used for blue-green switching."
  value       = aws_lb_listener.http.arn
}

output "blue_target_group_arn" {
  description = "ARN of the blue target group."
  value       = aws_lb_target_group.app["blue"].arn
}

output "green_target_group_arn" {
  description = "ARN of the green target group."
  value       = aws_lb_target_group.app["green"].arn
}

output "blue_direct_url" {
  description = "Direct URL of the blue instance."
  value       = "http://${aws_instance.app["blue"].public_ip}:5001"
}

output "green_direct_url" {
  description = "Direct URL of the green instance."
  value       = "http://${aws_instance.app["green"].public_ip}:5001"
}

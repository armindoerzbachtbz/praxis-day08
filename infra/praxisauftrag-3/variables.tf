variable "aws_region" {
  description = "AWS region for AWS Academy Learner Lab."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for created AWS resources."
  type        = string
  default     = "techstyle-pa3"
}

variable "student_name" {
  description = "Short name used to make AWS resource names unique."
  type        = string
  default     = "student"
}

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.30.0.0/16"
}

variable "public_subnet_cidr_blocks" {
  description = "CIDR blocks for the two public subnets used by the ALB."
  type        = list(string)
  default     = ["10.30.1.0/24", "10.30.2.0/24"]

  validation {
    condition     = length(var.public_subnet_cidr_blocks) >= 2
    error_message = "At least two public subnet CIDR blocks are required for the Application Load Balancer."
  }
}

variable "instance_type" {
  description = "EC2 instance type for blue and green."
  type        = string
  default     = "t3.micro"
}

variable "root_volume_size" {
  description = "Root volume size in GB."
  type        = number
  default     = 12
}

variable "ssh_public_key_path" {
  description = "Optional path to an SSH public key that will be added to the ubuntu user's authorized_keys via cloud-init."
  type        = string
  default     = ""
}

variable "allowed_ssh_cidr_blocks" {
  description = "CIDR blocks that are allowed to connect via SSH."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "direct_app_cidr_blocks" {
  description = "CIDR blocks allowed to access EC2 port 5001 directly for deployment verification."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "cloud_init_path" {
  description = "Path to the cloud-init file, relative to this Terraform folder."
  type        = string
  default     = "cloud-init.yml"

  validation {
    condition     = fileexists("${path.module}/${var.cloud_init_path}")
    error_message = "cloud_init_path must point to an existing cloud-init file."
  }
}

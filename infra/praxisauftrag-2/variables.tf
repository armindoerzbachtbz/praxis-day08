variable "aws_region" {
  description = "AWS region for AWS Academy Learner Lab."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for created AWS resources."
  type        = string
  default     = "techstyle-pa2"
}

variable "student_name" {
  description = "Short name used to make AWS resource names unique."
  type        = string
  default     = "student"
}

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr_block" {
  description = "CIDR block for the public subnet."
  type        = string
  default     = "10.0.1.0/24"
}

variable "instance_type" {
  description = "EC2 instance type."
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
  description = "CIDR blocks allowed to connect via SSH. Restrict this to your own public IP when possible."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "app_cidr_blocks" {
  description = "CIDR blocks allowed to access the TechStyle app on port 5001."
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

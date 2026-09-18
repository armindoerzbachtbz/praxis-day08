provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

locals {
  common_tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }

  colors             = toset(["blue", "green"])
  ssh_authorized_key = var.ssh_public_key_path != "" ? trimspace(file(pathexpand(var.ssh_public_key_path))) : ""
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.student_name}-vpc"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.student_name}-igw"
  })
}

resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr_blocks[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.student_name}-public-${count.index + 1}"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.student_name}-public-rt"
  })
}

resource "aws_route_table_association" "public" {
  count = 2

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-${var.student_name}-alb-sg"
  description = "Allow HTTP traffic to the TechStyle ALB."
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.student_name}-alb-sg"
  })
}

resource "aws_security_group" "app" {
  name        = "${var.project_name}-${var.student_name}-app-sg"
  description = "Allow SSH and app traffic for blue-green EC2 instances."
  vpc_id      = aws_vpc.main.id

  dynamic "ingress" {
    for_each = length(var.allowed_ssh_cidr_blocks) > 0 ? [1] : []

    content {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = var.allowed_ssh_cidr_blocks
    }
  }

  ingress {
    description     = "App traffic from ALB"
    from_port       = 5001
    to_port         = 5001
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    description = "Direct app access for pipeline health checks"
    from_port   = 5001
    to_port     = 5001
    protocol    = "tcp"
    cidr_blocks = var.direct_app_cidr_blocks
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.student_name}-app-sg"
  })
}

resource "aws_instance" "app" {
  for_each = local.colors

  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = each.key == "blue" ? aws_subnet.public[0].id : aws_subnet.public[1].id
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true
  user_data = templatefile("${path.module}/${var.cloud_init_path}", {
    ssh_authorized_key = local.ssh_authorized_key
    color              = each.key
  })
  user_data_replace_on_change = true

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
  }

  tags = merge(local.common_tags, {
    Name  = "${var.project_name}-${var.student_name}-${each.key}"
    Color = each.key
  })
}

resource "aws_lb" "app" {
  name               = "${var.project_name}-${var.student_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.student_name}-alb"
  })
}

resource "aws_lb_target_group" "app" {
  for_each = local.colors

  name     = "${var.project_name}-${var.student_name}-${each.key}"
  port     = 5001
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    path                = "/api/products"
    matcher             = "200"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = merge(local.common_tags, {
    Name  = "${var.project_name}-${var.student_name}-${each.key}-tg"
    Color = each.key
  })
}

resource "aws_lb_target_group_attachment" "app" {
  for_each = local.colors

  target_group_arn = aws_lb_target_group.app[each.key].arn
  target_id        = aws_instance.app[each.key].id
  port             = 5001
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app["blue"].arn
  }
}

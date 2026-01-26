# 1. The Virtual Private Cloud (VPC)
# This is the logically isolated network for HawkGrid
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16" # Provides 65,536 private IPs
  enable_dns_support   = true          # Essential for service discovery
  enable_dns_hostnames = true          # Required for ALB and EC2 naming

  tags = {
    Name = "${var.project_name}-VPC"
  }
}

# 2. Public Subnet
# For your Dashboard and Bastion nodes that need internet access
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true # Automatically assigns public IPs

  tags = {
    Name = "${var.project_name}-Public-Subnet"
  }
}

# 3. Private Subnet
# Where your sensitive "victim" workloads and data live
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${var.project_name}-Private-Subnet"
  }
}

# 4. Internet Gateway
# Allows traffic between your public subnet and the internet
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-IGW"
  }
}

# 5. Public Route Table
# Directs public subnet traffic to the Internet Gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "${var.project_name}-Public-RT"
  }
}

# 6. Route Table Association
# Connects the public subnet to the public route table
resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group for Victim Instance
resource "aws_security_group" "victim_sg" {
  name        = "hawkgrid-victim-sg"
  description = "Allow SSH and ICMP for HawkGrid demo"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "RDP from my laptop"
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["103.178.49.202/32"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
  description = "Allow ICMP (Ping)"
  from_port   = -1
  to_port     = -1
  protocol    = "icmp"
  cidr_blocks = ["0.0.0.0/0"]
}

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "hawkgrid_profile" {
  name = "hawkgrid-instance-profile"
  role = aws_iam_role.orchestrator_role.name
}

# EC2 Victim Instance
resource "aws_instance" "victim" {
  ami                         = "ami-06b5375e3af24939c" # Windows (us-east-1)
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.victim_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.hawkgrid_profile.name
  key_name                    = "project"
  associate_public_ip_address = true

  tags = {
    Name = "HawkGrid-Victim"
    Role = "HawkGrid-Attack-Target"
  }
}

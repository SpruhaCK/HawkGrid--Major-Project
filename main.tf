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
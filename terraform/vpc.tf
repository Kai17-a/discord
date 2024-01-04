# ---------------------------
# VPC
# ---------------------------
resource "aws_vpc" "discord_vpc"{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true   # DNSホスト名を有効化
  tags = {
    Name = "terraform-discord-vpc"
  }
}

# ---------------------------
# Subnet
# ---------------------------
resource "aws_subnet" "discord_public_1a_sn" {
  vpc_id = aws_vpc.discord_vpc.id
  cidr_block = "10.0.0.0/20"
  availability_zone = "${var.az_a}"

  tags = {
    Name = "terraform-discord-public-1a-sn"
  }
}

# ---------------------------
# Internet Gateway
# ---------------------------
resource "aws_internet_gateway" "discord_igw" {
  vpc_id = aws_vpc.discord_vpc.id
  tags = {
    Name = "terraform-discord-igw"
  }
}

# ---------------------------
# Route table
# ---------------------------
# Route table作成
resource "aws_route_table" "discord_public_rt" {
  vpc_id = aws_vpc.discord_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.discord_igw.id
  }
  tags = {
    Name = "terraform-discord-public-rt"
  }
}

# SubnetとRoute tableの関連付け
resource "aws_route_table_association" "discord_igw_public_rt_associate" {
  subnet_id = aws_subnet.discord_public_1a_sn.id
  route_table_id = aws_route_table.discord_public_rt.id
}

# ---------------------------
# Security Group
# ---------------------------
# 自分のパブリックIP取得
data "http" "ifconfig" {
  url = "http://ipv4.icanhazip.com/"
}

variable "allowed_cidr" {
  default = null
}

locals {
  myip = chomp(data.http.ifconfig.body)
  allowed_cidr  = (var.allowed_cidr == null) ? "${local.myip}/32" : var.allowed_cidr
}

# Security Group作成
resource "aws_security_group" "discord_ec2_sg" {
  name = "terraform-discord-ec2-sg"
  vpc_id = aws_vpc.discord_vpc.id
  tags = {
    Name = "terraform-discord-ec2-sg"
  }

  # インバウンドルール
  ingress {
    description = "SSH"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [local.allowed_cidr]
  }

  ingress {
    description = "Mincraft Port"
    from_port = 25565
    to_port = 25565
    protocol = "tcp"
    cidr_blocks = [local.allowed_cidr]
  }

  # アウトバウンドルール
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
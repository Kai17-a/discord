# ---------------------------
# EC2 Key pair
# ---------------------------
variable "key_name" {
  default = "discord-mincraft-skyblock-keypair"
}

# 秘密鍵のアルゴリズム設定
resource "tls_private_key" "discord_minecraft_skyblock_private_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# クライアントPCにKey pair（秘密鍵と公開鍵）を作成
# - Windowsの場合はフォルダを"\\"で区切る（エスケープする必要がある）
# - [terraform apply] 実行後はクライアントPCの公開鍵は自動削除される
locals {
  public_key_file  = ".\\private_key\\${var.key_name}.id_rsa.pub"
  private_key_file = ".\\private_key\\${var.key_name}.id_rsa"
}

resource "local_file" "discord_minecraft_skyblock_private_key_pem" {
  filename = "${local.private_key_file}"
  content  = "${tls_private_key.discord_minecraft_skyblock_private_key.private_key_pem}"
}

# 上記で作成した公開鍵をAWSのKey pairにインポート
resource "aws_key_pair" "discord_minecraft_skyblock_keypair" {
  key_name   = "${var.key_name}"
  public_key = "${tls_private_key.discord_minecraft_skyblock_private_key.public_key_openssh}"
}

# ---------------------------
# EC2
# ---------------------------
variable "ec2_ami" {
  default = "ami-0dfa284c9d7b2adad"
}

# EC2作成
resource "aws_instance" "discord_minecraft_skyblock_ec2" {
  ami = "${var.ec2_ami}"
  # instance_type = "t2.medium"
  instance_type = "t2.micro"
  availability_zone = "${var.az_a}"
  vpc_security_group_ids = [aws_security_group.discord_ec2_sg.id]
  subnet_id = aws_subnet.discord_public_1a_sn.id
  associate_public_ip_address = "true"
  key_name = "${var.key_name}"
  tags = {
    Name = "terraform-discord-minecraft-skyblock-ec2"
  }
  lifecycle {
    ignore_changes = [
      "ami",
    ]
  }
}

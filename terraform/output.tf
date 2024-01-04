# 作成したEC2のパブリックIPアドレスを出力
output "ec2_global_ips" {
  value = "${aws_instance.discord_minecraft_skyblock_ec2.*.public_ip}"
}
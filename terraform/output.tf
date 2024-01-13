# 作成したEC2のパブリックIPアドレスを出力
output "ec2_global_ips" {
  value = aws_instance.discord_minecraft_skyblock_ec2.public_ip
}

# 作成したStep FunctionsのArnを出力
output "stf_arn" {
  description = "Step Functions Arns"
  value = [
    "サーバー用: ${aws_sfn_state_machine.sfn_discord-server-manager-app_state_machine.arn}",
    "料金通知用: ${aws_sfn_state_machine.sfn_discord-notify-billing-app_state_machine.arn}",
  ]
}

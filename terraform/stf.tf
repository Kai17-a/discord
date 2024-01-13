resource "aws_sfn_state_machine" "sfn_discord-server-manager-app_state_machine" {
  name     = "sfn-discord-server-manager-app-statemachine"
  role_arn = "arn:aws:iam::785735044390:role/stf-lambda-role"

  definition = <<EOF
{
  "Comment": "discord ゲームサーバー起動",
  "StartAt": "server manager",
  "States": {
    "server manager": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ap-northeast-1:785735044390:function:discord-server-manager-function",
      "End": true
    }
  }
}
EOF
}

resource "aws_sfn_state_machine" "sfn_discord-notify-billing-app_state_machine" {
  name     = "sfn-discord-notify-billing-app-statemachine"
  role_arn = "arn:aws:iam::785735044390:role/stf-lambda-role"

  definition = <<EOF
{
  "Comment": "aws使用料金を取得",
  "StartAt": "notify-billing-app",
  "States": {
    "notify-billing-app": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ap-northeast-1:785735044390:function:notify-billing-function",
      "End": true
    }
  }
}
EOF
}
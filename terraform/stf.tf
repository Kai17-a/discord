resource "aws_sfn_state_machine" "sfn_state_machine" {
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


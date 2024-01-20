resource "aws_sfn_state_machine" "sfn_discord-server-manager-app_state_machine" {
  name     = "sfn-discord-server-manager-app-statemachine"
  role_arn = "${var.stf_lambda_role_arn}"

  definition = <<EOF
{
  "Comment": "discord ゲームサーバー起動",
  "StartAt": "ChoiceState",
  "States": {

    "ChoiceState": {
      "Type" : "Choice",
      "Choices": [
        {
          "Variable": "$.command_name",
          "StringEquals": "start",
          "Next": "ServerStartState"
        },
        {
          "Variable": "$.command_name",
          "StringEquals": "stop",
          "Next": "ServerStopState"
        },
        {
          "Variable": "$.command_name",
          "StringEquals": "status",
          "Next": "ServerStatusState"
        }
      ],
      "Default": "DefaultState"
    },

    "ServerStartState": {
      "Type": "Task",
      "Resource": "${var.discord_command_Arn_list.start}",
      "End": true
    },

    "ServerStopState": {
      "Type": "Task",
      "Resource": "${var.discord_command_Arn_list.stop}",
      "End": true
    },
    
    "ServerStatusState": {
      "Type": "Task",
      "Resource": "${var.discord_command_Arn_list.status}",
      "End": true
    },

    "DefaultState": {
      "Type": "Fail",
      "Cause": "No Matches!"
    }
  }
}
EOF
}

resource "aws_sfn_state_machine" "sfn_discord-notify-billing-app_state_machine" {
  name     = "sfn-discord-notify-billing-app-statemachine"
  role_arn = "${var.stf_lambda_role_arn}"

  definition = <<EOF
{
  "Comment": "aws使用料金を取得",
  "StartAt": "notify-billing-app",
  "States": {
    "notify-billing-app": {
      "Type": "Task",
      "Resource": "${var.aws_cost_lambda_arn}",
      "End": true
    }
  }
}
EOF
}
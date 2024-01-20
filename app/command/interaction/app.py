import os
from datetime import datetime
import logging
import json
import boto3
import discord_interactions
from discord_interactions import InteractionType, InteractionResponseType

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger()


stf_client = boto3.client('stepfunctions')
sqs_client = boto3.client('sqs')

def verify_request(event: dict) -> bool:
    """
    リクエストの署名検証
    
    Parameters
    ----------
    event : Any
        AWS Lambda イベント引数
    
    Returns
    -------
    verify_result : bool
        処理検証結果
    """
    body = event['body']
    headers = event['headers']
    signature = headers['x-signature-ed25519']
    timestamp = headers['x-signature-timestamp']
    publicKey = os.getenv('DISCORD_PUBLIC_KEY')
    if not body or not signature or not timestamp or not publicKey:
        logger.info("リクエスト情報が存在しません")
        return False
    if discord_interactions.verify_key(bytes(body, 'utf-8'), signature, timestamp, publicKey):
        return True
    else:
        logger.error("リクエスト検証に失敗しました")
        return False

def handle_interaction(interaction: dict) -> dict:
    """
    interaction の処理
    ここでslash commandsの振分け＆処理を行う
    
    Parameters
    ----------
    interaction : dict
        AWS Lambda イベント引数 body
    
    Returns
    -------
    content : dict
        discordレスポンス
    """

    if interaction['type'] is InteractionType.APPLICATION_COMMAND:
        # discordからのリクエストがslash commandsの場合
        channel_name = interaction['channel']['name']
        user_name = interaction['member']['user']['global_name']
        command_name = interaction['data']['name']
        channel_id = interaction['channel_id']

        if command_name == 'aws_cost':
            usable_channel_name = "aws_料金"
        else:
            usable_channel_name = "api実行"

        if usable_channel_name == "api実行":
            if channel_name != usable_channel_name:
                # コマンド実行が実行できるチャンネルか判定
                return {
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {
                        "content": f"このチャンネルでコマンドは実行できません。\n\"api実行\"チャンネルでコマンドを実行してください。\""
                    }
            }

            if command_name == 'start' or command_name == 'stop':
                execute_stepfunctios(os.getenv('SERVER_MANAGEMENT_STATEMACHINE_ARN'), user_name, command_name, channel_id)
                execute_send_sqs(channel_id, user_name, command_name)
                return {
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {
                        "content": f"/{command_name}コマンドが実行されました。\n実行者: {user_name}"
                    }
                }
        elif usable_channel_name == "aws_料金":
            if channel_name != usable_channel_name or interaction['member']['user']['id'] != '883638889259102248':
                # コマンド実行が実行できるチャンネルか判定
                return {
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {
                        "content": f"このコマンドの実行権限がありません。"
                    }
            }
            if command_name == 'aws_cost':
                execute_stepfunctios(os.getenv('NOTIRY_BILLING_STATEMACHINE_ARN'), user_name, command_name, channel_id, )
                execute_send_sqs(channel_id, user_name, command_name)
                return {
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {
                        "content": f"/{command_name}コマンドが実行されました。\n実行者: {user_name}"
                    }
                }
        else:
            return {
                "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": f"存在しないコマンドです。"
                }
            }
    else:
        return {
            "type": InteractionResponseType.PONG,
        }
    
def execute_stepfunctios(stf_arn, user_name='', command_name='', channel_id='') -> None:
    """
    ec2用のLambdaを実行するstepfunctionsを実行する
    
    Parameters
    ----------
    stf_arn: str
        step functions arn
    user_name : str
        コマンド実行ユーザー名
    command_name : str
        コマンド名
    channel_id : str
        コマンドを実行したDiscordチャンネルID
    """
    try:
        content = ''
        if user_name and command_name and channel_id:
            content = json.dumps({
                "user_name": user_name,
                "action": command_name,
                "channel_id": channel_id
            })
        stf_client.start_execution(stateMachineArn=stf_arn, input=content)
    except Exception as e:
        logger.error(f'StepFunctions連携処理が失敗しました。\nエラー内容：{e.__class__.__name__}')

def execute_send_sqs(channel_id: str, user_name: str, command_name: str) -> None:
    """
    監視ログ出力用のSQSへメッセージを送信する
    
    Parameters
    ----------
    channel_id : str
        コマンドを実行したDiscordチャンネルID
    user_name : str
        コマンド実行ユーザー名
    command_name : str
        コマンド名
    
    """
    queue_name = os.getenv('SQS_QUEUE_NAME')

    try:
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)
        body = {
            "channel_id": channel_id,
            "user": user_name,
            "command": command_name,
            "executed_at": datetime.now().isoformat()
        }
        sqs_client.send_message(QueueUrl=queue_url['QueueUrl'], MessageBody=json.dumps(body))
    except Exception as e:
        logger.error(f'SQS送信処理が失敗しました。\nエラー内容：{e.__class__.__name__}')

def lambda_handler(event, context):
    logger.info(event['body'])

    if not verify_request(event):
        return {
            "statusCode": 400,
        }
    else:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(handle_interaction(json.loads(event['body'])))
        }
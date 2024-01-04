import os
import datetime
import logging
import json
import boto3
import discord_interactions
from discord_interactions import InteractionType, InteractionResponseType

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger()

stf_client = boto3.client('stepfunctions')

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
    publicKey = os.getenv('DiscordPublicKey')
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
        user_name = interaction['member']['user']['global_name']
        command_name = interaction['data']['name']
        channel_id = interaction['channel_id']
        if command_name == 'start' or command_name == 'stop':
            execute_stepfunctios(user_name, command_name, channel_id)
            return {
                "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": f"コマンドが実行されました。\nコマンド: /{command_name}\n実行者: {user_name}\n実行時刻: {datetime.datetime.now()}"
                }
            }
        else:
            return {
                "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": f"存在しないコマンドが実行されました。\nコマンド: /{command_name}\n実行者: {user_name}\n実行時刻: {datetime.datetime.now()}"
                }
            }
    else:
        return {
            "type": InteractionResponseType.PONG,
        }
    
def execute_stepfunctios(user_name, command_name, channel_id):
    content = json.dumps({
        "user_name": user_name,
        "action": command_name,
        "channel_id": channel_id
    })
    stf_client.start_execution(stateMachineArn = os.getenv('StatemachineArn'), input=content)



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
import os
import logging
import json
import discord_interactions
from discord_interactions import InteractionType, InteractionResponseType

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger()

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
        command = interaction['data']
        if command['name'] == 'hello':
            return {
                "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": "hello Lambda!"
                }
            }
    else:
        return {
            "type": InteractionResponseType.PONG,
        }

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
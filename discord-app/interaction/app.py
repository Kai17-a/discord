import os
import logging
import json
import discord_interactions
from discord_interactions import InteractionType, InteractionResponseType

def verify_request(event) -> bool:
    """
    リクエストの署名検証
    
    Parameters
    ----------
    event : Any
        AWS Lambda イベント引数
    
    Returns
    -------
    verify_result : bool
        処刑検証結果
    """
    headers = event['headers']
    body = event['body']
    signature = headers['x-signature-ed25519']
    timestamp = headers['x-signature-timestamp']
    publicKey = os.getenv('DiscordPublicKey')
    if not body or not signature or not timestamp or not publicKey:
        return False
    return discord_interactions.verify_key(bytes(body, 'utf-8'), signature, timestamp, publicKey)

def handle_interaction(interaction):
    if interaction['type'] is InteractionType.APPLICATION_COMMAND:
        data = interaction['data']
        if data['name'] == 'hello':
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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s")
    logging.info(event['body'])

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
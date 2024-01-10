import os
import json
import requests
import logging
import boto3
from boto3.dynamodb.conditions import Attr

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger()
url = os.getenv('DISCORD_WEBHOOK_URL')
dynamodb = boto3.resource('dynamodb')

def get_dynamodb(channel_id: str):
    """
    dynamodb取得処理
    
    Parameters
    ----------
    channel_id : str
        discordチャンネルID
    
    Returns
    -------
    response : dict
        検索結果
    """
    table = dynamodb.Table('servers')
    response = table.scan(
        FilterExpression = Attr("channel_id").eq(channel_id)
    )
    return response

def post_discord(channel_name, user, command, executed_at):
    """
    webhook送信
    
    Parameters
    ----------
    channel_name : str
        チャンネル名
    user : str
        実行者名
    command : str
        コマンド
    executed_at : str
        実行日時
    """
    message = f"チャンネル名：{channel_name}\nコマンド：/{command}\n実行者：{user}"
    body = {
        "embeds": [{
            "description": message,
            "timestamp": executed_at
        }]
    }
    requests.post(url, json=body)

def lambda_handler(event, context):
    logger.info(event)
    print(event)
    input = json.loads(event['Records'][0]['body'])
    items = get_dynamodb(input['channel_id'])

    if items['Count'] == 0:
        logger.error("DB取得失敗")

    channel_name = items['Items'][0]['channel_name']
    user = input['user']
    command = input['command']
    executed_at = input['executed_at']
    post_discord(channel_name, user, command, executed_at)
import requests
import logging
import boto3
from boto3.dynamodb.conditions import Attr

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger()
region = 'ap-northeast-1'
ec2 = boto3.client('ec2', region_name=region)
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

def post_discord(url: str, user_name: str, message: str):
    """
    webhook送信
    
    Parameters
    ----------
    url : str
        webhook_url
    user_name : str
        API実行者名
    message : str
        メッセージ
    """
    body = {
        "content": f"{message}\n実行者: {user_name}",
    }
    requests.post(url, json=body)

def lambda_handler(event, context):
    logger.debug(event)
    
    items = get_dynamodb()
    instances = [items["Items"][0]["instance_id"]]
    response = ec2.describe_instances(InstanceIds=instances)
    
    ec2_status = response['Reservations'][0]['Instances'][0]['State']['Name']
    action = event["action"]
    user_name = event["user_name"]
    url = items["Items"][0]["webhook_url"]

    if action == "start" and ec2_status == "stopped":
        ec2.start_instances(InstanceIds=instances)
        post_discord(url, user_name, "サーバー起動中です。")
    elif action == "stop" and ec2_status == "running":
        ec2.stop_instances(InstanceIds=instances)
        post_discord(url, user_name, "サーバー停止中です。")
    else:
        logger.error("不正な値")
        post_discord(url, user_name, "処理に失敗しました。\nサーバーの状態とコマンドを確かめてください。")


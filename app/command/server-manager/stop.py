import requests
import logging
import boto3
import math
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger()

JST = timezone(timedelta(hours=+9), 'JST')

ec2 = boto3.client('ec2', region_name='ap-northeast-1')
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

def update_dynamodb(channel_id: str, instance_id: str, started_at: str):
    utilization_time = get_utilization_time(started_at)
    table = dynamodb.Table('servers')

    try:
        option = {
            'Key': {'instance_id': instance_id},
            'ConditionExpression': '#channel_id = :channel_id',
            'UpdateExpression': 'set #is_active = :is_active, #utilization_time = :utilization_time',
            'ExpressionAttributeNames': {
                '#channel_id': 'channel_id',
                '#is_active': 'is_active',
                '#utilization_time': 'utilization_time'
            },
            'ExpressionAttributeValues': {
                ':channel_id': channel_id,
                ':is_active': False,
                ':utilization_time': utilization_time
            }
        }
        table.update_item(**option)

    except Exception as err:
        logger.error(
                "%sの更新に失敗しました。エラーコード: %s, エラーメッセージ: %s",
                table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
        

def get_utilization_time(started_at: str):
    date_format = '%Y-%m-%d %H:%M:%S'
    dt_started_at = datetime.strptime(started_at, date_format)
    dt_now = datetime.strptime(datetime.now(JST).strftime(date_format), date_format)

    return math.ceil((dt_now - dt_started_at).seconds / 3600)

def post_discord(url: str, message: str):
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
        "embeds": [{
            "description": message,
        }],
    }
    requests.post(url, json=body)

def lambda_handler(event, context):
    logger.debug(event)
    
    try:
        channel_id = event["channel_id"]

        items = get_dynamodb(channel_id)
        if items["Count"] == 0:
            logger.error("サーバーが存在しない")
            raise Exception('サーバーが存在しません')

        instances = [items["Items"][0]["instance_id"]]
        response = ec2.describe_instances(InstanceIds=instances)

        ec2_status = response['Reservations'][0]['Instances'][0]['State']['Name']

        if ec2_status == 'running' or ec2_status == 'stopping':
            ec2.stop_instances(InstanceIds=instances)
            update_dynamodb(channel_id=channel_id, instance_id=instances[0], started_at=items["Items"][0]["started_at"])
            message = f'サーバーを停止中です'
        elif ec2_status == 'stopped':
            message = f'サーバーは既に停止しています'
            logger.warn(message)
        else:
            message = f'コマンドでエラーが発生しました'
            logger.error(message)

        post_discord(items["Items"][0]['webhook_url'], message)

    except Exception as e:
        logger.error(f'エラーが発生しました。\nエラー内容：{e.__class__.__name__}')
        raise RuntimeError('処理失敗') from e

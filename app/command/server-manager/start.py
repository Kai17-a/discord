import requests
import logging
import boto3
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

def update_dynamodb(channel_id: str, instance_id: str):
    dt_now = datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')
    table = dynamodb.Table('servers')
    try:
        option = {
            'Key': {'instance_id': instance_id},
            'ConditionExpression': '#channel_id = :channel_id',
            'UpdateExpression': 'set #is_active = :is_active, #started_at = :started_at',
            'ExpressionAttributeNames': {
                '#channel_id': 'channel_id',
                '#is_active': 'is_active',
                '#started_at': 'started_at'
            },
            'ExpressionAttributeValues': {
                ':channel_id': channel_id,
                ':is_active': True,
                ':started_at': dt_now
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
            logger.error("サーバーが存在しません")
            raise Exception('サーバーが存在しません')

        instances = [items["Items"][0]["instance_id"]]
        response = ec2.describe_instances(InstanceIds=instances)

        ec2_status = response['Reservations'][0]['Instances'][0]['State']['Name']

        if ec2_status == "stopped" or ec2_status == "pending":
            ec2.start_instances(InstanceIds=instances)
            update_dynamodb(channel_id, instance_id=instances[0])
            message = f'サーバーを起動中です'
        elif ec2_status == "running":
            logger.warn("サーバーは既に起動しています")
            message = f'サーバーは既に起動しています'
        else:
            logger.error("想定外のステータス")
            message = f'コマンドエラー'

        post_discord(items["Items"][0]['webhook_url'], message)
        
    except Exception as e:
        logger.error(f'エラーが発生しました。\nエラー内容：{e.__class__.__name__}')
        raise RuntimeError('処理失敗') from e

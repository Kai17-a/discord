import requests
import logging
import boto3
from boto3.dynamodb.conditions import Attr

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger()

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
        items = get_dynamodb(event["channel_id"])
        if items["Count"] == 0:
            logger.error("サーバーが存在しません")
            raise Exception('サーバーが存在しません')

        instances = [items["Items"][0]["instance_id"]]
        response = ec2.describe_instances(InstanceIds=instances)

        ec2_status = response['Reservations'][0]['Instances'][0]['State']['Name']

        if ec2_status == "stopped":
            ec2.start_instances(InstanceIds=instances)
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

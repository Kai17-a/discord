import os
import logging
import boto3

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger()

region = 'ap-northeast-1'
instances = [os.environ['INSTANCE_ID']]

def get_dynamodb():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('sample1')
    response = table.get_item(
        Key = {
            'name': "name",
        }
    )

    return ""

def get_instance_id():
    # dynamoDbから取得
    return ""

def post_discord():
    # dynamoDbから取得
    return ""

def lambda_handler(event, context):
    logger.info("")

    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances(InstanceIds=instances)
    ec2_status = response['Reservations'][0]['Instances'][0]['State']['Name']

    action = event["Action"]
    if action == "start" and ec2_status == "stopped":
        ec2.start_instances(InstanceIds=instances)
    elif action == "stop"and ec2_status == "running":
        ec2.stop_instances(InstanceIds=instances)
    else:
        logger.error("不正な値")


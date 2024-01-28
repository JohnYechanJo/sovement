import boto3
import json
from datetime import datetime, timedelta

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    timestamp = str((datetime.now() - timedelta(hours=9)).timestamp())
    response = dynamodb.put_item(
        TableName='iot-repair-request',
        Item={
            'deviceID': {'S': event['deviceCode']},
            'timestamp': {'S': timestamp},
            'name': {'S': event['name']},
            'phone': {'S': event['phone']},
            'repairType': {'S': event['type']},
            'imgUrl': {'S': event['imgUrl']},
            'content': {'S': event['content']},
            'complete': {'BOOL': False}
        })
    
    return {
        'body': 'success'
    }

import boto3
import json
from datetime import datetime

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    timestamp = str(int(datetime.now().timestamp()))

    response = dynamodb.put_item(
        TableName='keco-alert',
        Item={
            'id': {'S': timestamp},
            'name': {'S': event['name']},
            'belong': {'S': event['belong']},
            'position': {'S': event['position']},
            'phone': {'S': event['phone']},
            'setting': {'S': event['setting']},
        })
    
    return {
        'body': 'success'
    }

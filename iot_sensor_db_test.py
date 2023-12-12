import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from dotenv import load_dotenv
import random
import time
import os

load_dotenv()

# AWS DynamoDB CLIENT 설정
dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name=os.getenv('AWS_REGION_NAME')
)

# 테이블 이름
table_name = os.getenv('DYNAMODB_TABLE_NAME')

# timestamp(초까지)
timestamp = str(int(datetime.now().timestamp()))

for i in range(15):
    # timestamp는 현재, 센서값은 랜덤
    timestamp = str(int(datetime.now().timestamp()))
    temp = str(random.randrange(15, 80))
    humid = str(random.randrange(0, 10))

    # 저장할 데이터 리스트
    items_to_put = [
        {
            # 기기 ID
            'deviceID': {'S': 'testDevice1'},
            # 센서 종류 + timestamp
            'sensorID_timestamp': {'S': 'T_' + timestamp},
            # 센서 측정 값
            'value': {'N': temp},
        },
        # {
        #     'deviceID': {'S': 'testDevice1'},
        #     'sensorID_timestamp': {'S': 'H_' + timestamp},
        #     'value': {'N': humid},
        # },
    ]

    # batch_write_item 요청 양식
    batch_items = [{
        'PutRequest': {
            'Item': item
        }
    } for item in items_to_put]

    try:
        # DynamoDB에 데이터들 추가
        response = dynamodb.batch_write_item(
            RequestItems={
                table_name: batch_items
            }
        )
        print("저장 완료:", response)
    except ClientError as e:
        print("오류 발생:", e)

    time.sleep(10)

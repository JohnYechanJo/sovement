from fastapi import FastAPI
from dotenv import load_dotenv
import asyncio
import os
import boto3
from collections import deque

# 백엔드 설정
app = FastAPI()
load_dotenv()

# AWS SMS CLIENT 설정
sns = boto3.client(
    "sns",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name=os.getenv('AWS_REGION_NAME_SNS')
)

# AWS DynamoDB CLIENT 설정
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name=os.getenv('AWS_REGION_NAME_DB')
)
# IoT 디바이스의 sensor 값이 있는 테이블과 정보가 있는 테이블 불러오기
sensor_table = dynamodb.Table(os.getenv('DYNAMODB_SENSOR_TABLE_NAME'))
information_table = dynamodb.Table(os.getenv('DYNAMODB_INFORMATION_TABLE_NAME'))

# 예시 기본 테이블 값 설정
test1_device_id = 'testDevice1'
test1_temperature_sensor_id = 'T_'
test1_temp_queue = deque([25, 30, 25, 30, 25, 30, 25, 30, 25, 30])
test1_device_information = information_table.query(
        KeyConditionExpression='#pk = :pk',
        ExpressionAttributeNames={'#pk': 'deviceID'},
        ExpressionAttributeValues={':pk': test1_device_id},
    )['Items'][0]
test1_admin_phone_number = test1_device_information['adminPhoneNumber']
test1_device_name = test1_device_information['deviceName']


# 10초마다 DynamoDB 데이터 가져와서 화재 발생 판단
async def get_temperature_data_from_dynamodb(
        device_id, temperature_sensor_id, temp_queue, admin_phone_number, device_name):
    # 연속으로 문자 전송되는 것을 방지하기 위한 화재 주의, 화재 발생 알림 문자를 전송했는지 여부
    send_alert = False
    send_fire = False

    while True:
        # test 디바이스의 가장 최근에 저장된 temperature sensor 값을 가져온다
        response = sensor_table.query(
            KeyConditionExpression='#pk = :pk AND begins_with(#sk, :sk)',
            ExpressionAttributeNames={'#pk': 'deviceID', '#sk': 'sensorID_timestamp'},
            ExpressionAttributeValues={':pk': device_id, ':sk': temperature_sensor_id},
            ScanIndexForward=False,
            Limit=1,
        )

        temp = response['Items'][0]['value']
        temp_average = sum(temp_queue) / 10

        # 화재 판별 로직
        if temp < temp_average - 10:
            send_alert = False
            send_fire = False
            pass

        elif temp_average - 10 <= temp < temp_average + 20:
            send_alert = False
            send_fire = False
            temp_queue.append(temp)
            temp_queue.popleft()

        elif temp_average + 20 <= temp < 70:
            if not send_alert:
                # 아래의 주석 처리 해제 시 디바이스 관리자의 번호로 문자 전송
                # sns.publish(
                #     PhoneNumber='+82' + admin_phone_number,
                #     Message=device_name + '의 온도가 높으니 확인 바랍니다.'
                # )
                print("화재 주의 문자 전송")
            send_alert = True
            print(device_name + '의 온도가 높으니 확인 바랍니다.')
        else:
            if not send_fire:
                # 아래의 주석 처리 해제 시 디바이스 관리자의 번호로 문자 전송
                # sns.publish(
                #     PhoneNumber='+82' + admin_phone_number,
                #     Message=device_name + '에서 화재가 발생했습니다.'
                # )
                print("화재 발생 문자 전송")
            send_alert = True
            send_fire = True
            print(device_name + '에서 화재가 발생했습니다.')

        print("온도: " + str(temp))

        await asyncio.sleep(10)  # 10초 대기


# API 엔드포인트
@app.get("/")
async def root():
    return {"message": "Working"}


# 비동기 작업 시작
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(
        get_temperature_data_from_dynamodb(
            test1_device_id, test1_temperature_sensor_id, test1_temp_queue, test1_admin_phone_number, test1_device_name
        )
    )

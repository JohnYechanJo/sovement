import boto3
from datetime import datetime, timedelta
import time

dynamodb = boto3.resource('dynamodb')

sensor_table = dynamodb.Table('iot-sensor-1')
information_table = dynamodb.Table('iot-information')


def dynamodb_information_update(device_id, attr_name, attr_value):
    key = {'deviceID': device_id}
    update_expression = 'SET #attrName = :attrValue'
    expression_attribute_names = {'#attrName': attr_name}
    expression_attribute_values = {':attrValue': attr_value}

    information_table.update_item(
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
    )


def get_temperature_data_from_dynamodb(device_id, temp_queue, admin_phone_number, device_name, alert, fire, fireAlert, network):
    # test 디바이스의 가장 최근에 저장된 temperature sensor 값을 가져온다
    response = sensor_table.query(
        KeyConditionExpression='#pk = :pk',
        ExpressionAttributeNames={'#pk': 'deviceID'},
        ExpressionAttributeValues={':pk': device_id},
        ScanIndexForward=False,
        Limit=1,
    )

    sensor_timestamp = int(response['Items'][0]['timestamp'])
    now = (datetime.now() - timedelta(minutes=1)).timestamp()

    if now > sensor_timestamp:
        if network:
            dynamodb_information_update(device_id, 'network', False)
    else:
        if not network:
            dynamodb_information_update(device_id, 'network', True)

        temp = response['Items'][0]['temperature']
        temp_average = sum(temp_queue) / 10
    
        # 화재 판별 로직
        if temp < temp_average - 10:
            if fireAlert != 'none':
                dynamodb_information_update(device_id, 'fireAlert', 'none')
    
        elif temp_average - 10 <= temp < temp_average + 20:
            if fireAlert != 'none':
                dynamodb_information_update(device_id, 'fireAlert', 'none')
    
            temp_queue = temp_queue[1:]
            temp_queue.append(temp)
    
            dynamodb_information_update(device_id, 'tempQueue', temp_queue)
    
        elif temp_average + 20 <= temp < 70:
            if fireAlert == 'none':
                # 아래의 주석 처리 해제 시 디바이스 관리자의 번호로 문자 전송
                # sns.publish(
                #     PhoneNumber='+82' + admin_phone_number,
                #     Message=device_name + '의 온도가 높으니 확인 바랍니다.'
                # )
                alert += 1
                dynamodb_information_update(device_id, 'alert', alert)
                dynamodb_information_update(device_id, 'fireAlert', 'caution')

        else:
            if fireAlert != 'warning':
                # 아래의 주석 처리 해제 시 디바이스 관리자의 번호로 문자 전송
                # sns.publish(
                #     PhoneNumber='+82' + admin_phone_number,
                #     Message=device_name + '에서 화재가 발생했습니다.'
                # )
                fire += 1
                dynamodb_information_update(device_id, 'fire', fire)
                dynamodb_information_update(device_id, 'fireAlert', 'warning')
    

def lambda_handler(event, context):
    devices_information = information_table.scan()['Items']

    for i in range(6):
        for device in devices_information:
            if device['active']:
                get_temperature_data_from_dynamodb(
                    device['deviceID'], device['tempQueue'], device['adminPhoneNumber'], device['deviceName'],
                    device['alert'], device['fire'], device['fireAlert'], device['network']
                )
        time.sleep(10)

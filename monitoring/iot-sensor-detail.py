import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
sensor_table = dynamodb.Table('iot-sensor-1')
information_table = dynamodb.Table('iot-information')


def lambda_handler(event, context):
    response = information_table.query(
                KeyConditionExpression='#pk = :pk',
                ExpressionAttributeNames={'#pk': 'deviceID'},
                ExpressionAttributeValues={':pk': event['params']['path']['id']},
                ScanIndexForward=False,
                Limit=1,
            )
    device = response['Items'][0]
    
    response = sensor_table.query(
                KeyConditionExpression='#pk = :pk',
                ExpressionAttributeNames={'#pk': 'deviceID'},
                ExpressionAttributeValues={':pk': device['deviceID']},
                ScanIndexForward=False,
                Limit=1,
            )
    current_value = response['Items'][0]
            
    probability = 'low'
    amount = 0
    battery = 'low'

    humid = current_value['humidity']
    # 습도 판별 로직
    if humid < 30:
        probability = 'high'
    elif humid < 55:
        probability = 'mid'
    else:
        probability = 'low'

    # 담배 꽁초 양
    distance = current_value['distance']
    amount = int((309 - distance) / 309 * 100)
    
    # 배터리 상태
    saved_datetime = datetime.strptime(device['battery'], "%y / %m / %d")
    current_date = datetime.now()
    difference = current_date - saved_datetime
    days_difference = difference.days
    
    if days_difference <= 1:
        battery = 'high'
    elif days_difference <= 3:
        battery = 'medium'
    else:
        battery = 'low'
        
    # 수거량 그래프
    time_intervals = [2, 4, 6, 8, 10, 24, 26, 28, 30, 32, 34]
    current_time = datetime.now()
    amount_data = []
    amount_data.append(amount)
    
    for interval in time_intervals:
        target_time = current_time - timedelta(hours=interval)
        timestamp = str(int(target_time.timestamp()))

        response = sensor_table.query(
            KeyConditionExpression='#pk = :pk AND #timestamp < :timestamp',
            ExpressionAttributeNames={'#pk': 'deviceID', '#timestamp': 'timestamp'},
            ExpressionAttributeValues={':pk': device['deviceID'], ':timestamp': timestamp},
            Limit=1,
            ScanIndexForward=False,
        )

        prev_amount = int((309 - response['Items'][0]['distance']) / 309 * 100)
        amount_data.append(prev_amount)
    
    # 어제 대비 수거량
    amount_yesterday = (amount_data[0] - amount_data[5]) - (amount_data[6] - amount_data[11])
    
    bin_info = {
                'device_name': device['deviceName'],
                'address': device['address'],
                'network': device['network'],
                'amount': amount,
                'probability': probability,
                'fire_alert': device['fireAlert'],
                'management_code': device['managementCode'],
                'last_battery': device['battery'],
                'battery': battery,
                'amount_yesterday': amount_yesterday,
                'amount_data': amount_data
            }
    
    return {
        "body": bin_info
    }



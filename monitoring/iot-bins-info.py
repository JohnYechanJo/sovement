import boto3

dynamodb = boto3.resource('dynamodb')
sensor_table = dynamodb.Table('iot-sensor-1')
information_table = dynamodb.Table('iot-information')


def lambda_handler(event, context):
    bins_info = []
    devices_information = information_table.scan()['Items']

    for device in devices_information:
        if device['active']:
            probability = 'low'
            amount = 0
            
            response = sensor_table.query(
                KeyConditionExpression='#pk = :pk',
                ExpressionAttributeNames={'#pk': 'deviceID'},
                ExpressionAttributeValues={':pk': device['deviceID']},
                ScanIndexForward=False,
                Limit=1,
            )
            
            humid = response['Items'][0]['humidity']
            # 습도 판별 로직
            if humid < 30:
                probability = 'high'
            elif humid < 55:
                probability = 'mid'
            else:
                probability = 'low'
        
            # 담배 꽁초 양
            distance = response['Items'][0]['distance']
            amount = int((309 - distance) / 309 * 100)
            
            bin_info = {
                'device_name': device['deviceName'],
                'device_id': device['deviceID'],
                'address': device['address'],
                'latitude': device['latitude'],
                'longitude': device['longitude'],
                'network': device['network'],
                'amount': amount,
                'probability': probability,
                'fire_alert': device['fireAlert'],
                'management_code': device['managementCode'],
                'admin': device['admin'],
                'install_date': device['installDate'],
            }
    
            bins_info.append(bin_info)

    return {
        'body': bins_info
    }



import boto3
import json
import base64
import hashlib
from datetime import datetime, timedelta
from requests_toolbelt.multipart import decoder

BUCKET_NAME = 'iot-monitoring-image'

response  = {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    },
    'body': ''
}
    

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    hash_salt = str(datetime.utcnow())
    file_path = 'repair'
    file_salt = hashlib.sha224(hash_salt.encode()).hexdigest()
    file_name = f'000{file_salt[:10].upper()}-{file_salt[10:15].upper()}-{file_salt[15:20].upper()}-{file_salt[20:25].upper()}'
    full_name = file_path + '/' + file_name + '.jpg'
    res_data = ''
    content = ''
    headers = ''
    
    body = base64.b64decode(event['body']) 
    
    if 'content-type' in event['headers']:
        content_type = event['headers']['content-type']
    else:
        content_type = event['headers']['Content-Type']
    
    decode = decoder.MultipartDecoder(body,content_type)
        
    for part in decode.parts:
        content = part.content
        headers = part.headers
        print(part.__dict__)
    
    try:
        s3_response = s3.put_object(Bucket=BUCKET_NAME, Key=full_name, Body=content)
    except Exception as e:
        raise IOError(e)
    response['body'] = json.dumps({'url' : f'https://iot-monitoring-image.s3.ap-northeast-2.amazonaws.com/{file_path}/{file_name}.jpg'})
    return response

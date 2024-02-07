import boto3
import json

dynamodb = boto3.resource('dynamodb')
keco_alert_table = dynamodb.Table('keco-alert')

def lambda_handler(event, context):
    key = {'id': event['params']['path']['id']}
    update_expression = 'SET #attrName1 = :attrValue1, #attrName2 = :attrValue2, #attrName3 = :attrValue3, #attrName4 = :attrValue4, #attrName5 = :attrValue5'
    expression_attribute_names = {'#attrName1': 'name', '#attrName2': 'belong', '#attrName3': 'position', '#attrName4': 'phone', '#attrName5': 'setting'}
    expression_attribute_values = {':attrValue1': event['body-json']['name'], ':attrValue2': event['body-json']['belong'], ':attrValue3': event['body-json']['position'], ':attrValue4': event['body-json']['phone'], ':attrValue5': event['body-json']['setting']}

    keco_alert_table.update_item(
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
    )
    
    return {
        'body': 'success'
    }

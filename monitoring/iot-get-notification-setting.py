import boto3

dynamodb = boto3.resource('dynamodb')
keco_alert_table = dynamodb.Table('keco-alert')


def lambda_handler(event, context):
    alerts_info = []
    alert_information = keco_alert_table.scan()['Items']

    for alert in alert_information:
        alert_info = {
            'id': alert['id'],
            'name': alert['name'],
            'belong': alert['belong'],
            'position': alert['position'],
            'phone': alert['phone'],
            'setting': alert['setting']
        }

        alerts_info.append(alert_info)

    return {
        'body': alerts_info,
    }


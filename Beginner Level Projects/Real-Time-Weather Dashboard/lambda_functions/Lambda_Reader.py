import json
import boto3
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMO_TABLE')
    table = dynamodb.Table(table_name)
    
    # Conusltamos a DynamoDB - Último Registro
    try:
        city = 'Lima'

        response = table.query(
            KeyConditionExpression=Key('city').eq(city),
            ScanIndexForward=False,  
            Limit=1
        )

        items = response.get('Items', [])

        if not items:
            return {
                'statusCode' : 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(
                    {'message' : 'No hay datos para Lima'}
                )
            }

        latest = items[0]
        latest['temp'] = float(latest['temp'])
        latest['humidity'] = float(latest['humidity'])
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(latest)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode' : 500,
            'headers' : {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }

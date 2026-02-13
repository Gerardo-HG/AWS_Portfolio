import boto3
import json
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get("TABLE_NAME")

table = dynamodb.Table(table_name)
id_counter = 'global_counter'

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters') or {}
        
        print(f"Query_params -> {query_params}")

        if query_params.get('type') == 'get':
            print("Operacion: SOLO LECTUA")
            visits = read_counter()
        else:
            print("Operacion: SOLO INCREMENTA")
            visits = increment_counter()

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json '},
            'body': json.dumps({'visits': int(visits)})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def read_counter():
    response = table.get_item(
        Key={'id': id_counter}
    )

    # If it does not exists, start with 0
    item = response.get('Item', {})
    visits = item.get('visits', 0)

    return visits

def increment_counter():
    response = table.update_item(
        Key={'id': id_counter},
        UpdateExpression='ADD visits :incremento',    
        ExpressionAttributeValues={':incremento': 1},
        ReturnValues='UPDATED_NEW'
    )

    visits = response['Attributes']['visits']
    return visits    
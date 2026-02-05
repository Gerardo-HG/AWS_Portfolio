import json
import boto3
import os
from boto3.dynamodb.conditions import Key
from decimal import Decimal

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMO_TABLE')
    table = dynamodb.Table(table_name)

    # 1. Obtener ID de la URL
    params = event.get('queryStringParameters')
    if not params or 'imageId' not in params:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Falta imageId'})}
    
    image_id = params['imageId']

    try:
        # 2. Consultar DynamoDB
        response = table.query(KeyConditionExpression=Key('imageId').eq(image_id))
        items = response.get('Items', [])

        if not items:
            return {'statusCode': 404, 'body': json.dumps({'message': 'Aun procesando o ID incorrecto'})}
            
        data = items[0]
        
        # 3. Generar Frase Amigable
        labels = data.get('Labels', [])
        if labels:
            nombres = [lbl['Name'] for lbl in labels[:5]] # Top 5 etiquetas
            frase = f"Hola! Según Rekognition, tu imagen contiene: {', '.join(nombres)}."
        else:
            frase = "No pude identificar objetos claros."

        # 4. Responder
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'mensaje': frase,
                'detalles': data
            }, default=str) 
        }

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


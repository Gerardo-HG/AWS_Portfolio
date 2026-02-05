import json
import boto3
import base64
import uuid
import os

def lambda_handler(event, context):
    bucket_name = os.environ.get('UPLOAD_BUCKET')
    s3 = boto3.client('s3')
    image_id = str(uuid.uuid4())
    
    try:
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            # limpia el base64 puro
            file_content = base64.b64decode(body)
        else:
            # Si envías binario directo
            file_content = body if isinstance(body, bytes) else body.encode('utf-8')

        # Detectar extensión original o usar .jpg por defecto
        file_name = f"{image_id}.jpg" 
        
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content, ContentType='image/jpeg')
        
        return {
            'statusCode': 200,
            'body': json.dumps({'imageId': image_id})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

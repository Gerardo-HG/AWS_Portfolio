import json, boto3, os, urllib.parse
from datetime import datetime
from decimal import Decimal

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        
        image_id = os.path.splitext(os.path.basename(key))[0]

        # REKOGNITION
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10,
            MinConfidence=75
        )

        # LIMPIEZA PARA DYNAMODB (Convierte floats a Decimal)
        labels_json = json.dumps(response['Labels'])
        labels_decimal = json.loads(labels_json, parse_float=Decimal)

        table = dynamodb.Table(os.environ['<YOUR_DYNAMO_TABLE_ENVIRONMENT_VARIABLE>'])
        table.put_item(Item={
            'imageId': image_id,
            'imageName': key,
            'Labels': labels_decimal,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return {'statusCode': 200}
    except Exception as e:
        print(f"ERROR CRÍTICO: {str(e)}")
        return {'statusCode': 500, 'body': str(e)}

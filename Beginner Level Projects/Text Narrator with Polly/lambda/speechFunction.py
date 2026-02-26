import json
import boto3
import base64
import uuid
from botocore.exceptions import ClientError

def lambda_handler(event, context):

    # Amazon Polly
    polly = boto3.client('polly')

    # Amazon S3
    s3 = boto3.client('s3')
    BUCKET_NAME = "audio-urls-gerardo-gg"

    # Web App    
    try:
        body = event.get('body', '{}')
        if isinstance(body, str):
            body_dict = json.loads(body)

        else:
            body_dict = body
    except Exception:
        body_dict = {}

    text = body_dict.get('text', '')

    if not text:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'El campo "text" es obligatorio'
            })
        }
    
    try:
        #LLamada a Polly
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Lucia',
            Engine='neural'
        )

        # Preparamos archivo en S3
        file_name = f"audio-{uuid.uuid4()}.mp3"

        # Guardamos en S3 el audio
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=response['AudioStream'].read(),
            ContentType='audio/mpeg'
        )

        # Generamos el URL firmado
        audio_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': file_name
            },
            ExpiresIn=3600
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(
                {
                    'url': audio_url,
                    'key': file_name
                }
            )
        }
    
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(
                {
                    'error': f"Error AWS: {e.response['Error']['Code']}"
                }
            )
            
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'error': str(e)}
            )
        }
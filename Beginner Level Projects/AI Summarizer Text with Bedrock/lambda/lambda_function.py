import json
import boto3

def lambda_handler(event, context):
    bedrock = boto3.client(service_name='bedrock-runtime')

    try:
        body = event.get('body', '{}')
        body_dict = json.loads(body)

        text_to_summarize = body_dict.get('text','')

        input_data = {
            'inputText': f"Resume el siguiente texto de forma clara en 3 líneas: {text_to_summarize}",
            'textGenerationConfig': {
                'maxTokenCount': 300,
                'temperature': 0,
                'topP':0.9
            }
        }

        response_model = bedrock.invoke_model(
            body=json.dumps(input_data),
            modelId='amazon.titan-text-express-v1:1',
            accept="application/json",
            contentType='application/json'
        )

        response_body = json.loads(response_model.get('body').read())

        resumen = response_body.get('results')[0].get('outputText')

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin':'*'
            },
            'body': json.dumps(
                {'resumen': resumen}
            )
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin':'*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
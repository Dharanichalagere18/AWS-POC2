import json
import uuid
import boto3
import base64
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
bucket_name = 'dncs3bucket'

def generate_presigned_url(file_name):
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=300 
        )
        return response
    except ClientError as e:
        raise Exception(f"Error generating pre-signed URL: {str(e)}")

def lambda_handler(event, context):
    http_method = event['httpMethod']

    if http_method == 'GET':
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            files = [obj['Key'] for obj in response.get('Contents', [])]
            
            return {
                'data': json.dumps({
                    'files': files
                })
            }
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': str(e)
                })
            }

    elif http_method == 'POST':
        try:

            if 'body' in event and 'file_based_64' in event['body']:
                base64_filecontent = event['body']['file_based_64']
                file_content = base64.b64decode(base64_filecontent)
                
               
                file_name = event['body'].get('filename') or f"{str(uuid.uuid4())}.txt"

                
                s3_client.put_object(Body=file_content, Bucket=bucket_name, Key=file_name)
                s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
                
                return {
                    'data': json.dumps({
                            'statusCode':201,
                            's3_url': s3_url
                        
                    })
                }
            elif 'body' in event and 'file' in event['body']:
                file_name = event['body']['file']
                presigned_url = generate_presigned_url(file_name)
                
                return {
                    'body': json.dumps({
                        'file-url': presigned_url
                    })
                }
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': 'Invalid request payload'
                    })
                }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': str(e)
                })
            }

    elif http_method == 'DELETE':
        try:
            if 'body' in event:
                file_name = event['body'].get('file')  

                s3_client.delete_object(Bucket=bucket_name, Key=file_name)
                
                return {
                    'statusCode': 201,
                    'body': json.dumps({
                        'status': f"{file_name} deleted successfully"
                    })
                }
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': 'Invalid request payload'
                    })
                }
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': str(e)
                })
            }

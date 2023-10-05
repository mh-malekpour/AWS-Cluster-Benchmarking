import sys
import boto3

def create_aws_service(service, region, secret_access_id, session_token, secret_access_key):
    try:
        aws_service = boto3.client(
            service_name=service,
            region_name=region,
            aws_access_key_id=secret_access_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        return aws_service

import json
import shutil
from datetime import datetime


def create_bucket(s3, bucket):
    timestamp = str(int(datetime.timestamp(datetime.now())))
    response = s3.create_bucket(Bucket=bucket + timestamp)
    bucket_name = response['Location'][1:]
    print(f'S3 bucket created: {bucket_name}')
    return bucket_name


def put_bucket_policy(s3, bucket_policy, bucket, aws_user_account, role_arn) -> None:
    bucket_policy['Statement'][0]['Principal'] = {"AWS": [aws_user_account]}
    bucket_policy['Statement'][0]['Resource'] = f'arn:aws:s3:::{bucket}/*'
    bucket_policy['Statement'][1]['Principal'] = {"AWS": [role_arn]}
    bucket_policy['Statement'][1]['Resource'] = f'arn:aws:s3:::{bucket}/*'
    s3.put_bucket_policy(
            Bucket=bucket,
            Policy=json.dumps(bucket_policy)
        )

    print(f'Policy applied to {bucket}')


def upload_server_app_to_s3_bucket(s3, bucket: str) -> None:
    shutil.make_archive('server', 'zip', 'flask')
    s3.upload_file('./server.zip', bucket, 'server.zip')
    print(f'Flask app uploaded to{bucket}')


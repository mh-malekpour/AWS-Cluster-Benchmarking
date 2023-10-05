# Read AWS credentials from the aws_credentials.txt file
with open('aws_credentials.txt', 'r') as file:
    lines = file.readlines()
    aws_credentials = {}
    for line in lines:
        key, value = line.strip().split('=')
        aws_credentials[key] = value

REGION = aws_credentials.get('region', 'us-east-1')
aws_access_key_id = aws_credentials['aws_access_key_id'],
aws_secret_access_key = aws_credentials['aws_secret_access_key'],
aws_session_token = aws_credentials.get('aws_session_token', None),

TAGS = {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'n_clustor', 'Value': '', },
                    {'Key': 'n_instance', 'Value': '', }  
                ]
            }
        

PROFILE ='LabInstanceProfile'

EC2_CONFIG= {
    'service_name': 'ec2', 
    'security_group': 'my_sec_group', 
    'key_pair' : 'my_key_pair', 
    'image_id' : 'ami-02538f8925e3aa27a', # get this using a commad run in aws
    'clustor_1':{
        'instance_type': 'm4.large', 
        'availability_zone': 'us-east-1a'

    }, 
    'clustor_2':{
        'instance_type': 't2.large', 
        'availability_zone' : 'us-east-1b'
    }
}

ELB_CONFIG = {
    'service_name': 'elbv2',
    'cluster1': {
        't_group_name': 'cluster1',
    },
    'cluster2': {
        't_group_name': 'cluster2',
    }
}


IAM_CONFIG = {
    'service_name': 'iam'
}
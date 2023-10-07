# Read AWS credentials from the aws_credentials.txt file
with open('aws_credentials.txt', 'r') as file:
    lines = file.readlines()
    aws_credentials = {}
    for line in lines:
        key, value = line.strip().split('=')
        aws_credentials[key] = value

REGION = aws_credentials.get('region', 'us-east-1')
aws_access_key_id = aws_credentials['aws_access_key_id']
aws_secret_access_key = aws_credentials['aws_secret_access_key']
aws_session_token = aws_credentials.get('aws_session_token', None)

# Tag template for the target groups (i.e the clusters)
TAGS = {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'n_clustor', 'Value': '', },
                    {'Key': 'n_instance', 'Value': '', }  
                ]
            }
        

# The profile
PROFILE ='LabInstanceProfile'

EC2_CONFIG= {
    'service_name': 'ec2', 
    'security_group': 'my_sec_group', 
    'key_pair' : 'my_key_pair', 
    'cluster_1':{
        'instance_type': 'm4.large', 
        'availability_zone': 'us-east-1a'

    }, 
    'cluster_2':{
        'instance_type': 't2.large', 
        'availability_zone' : 'us-east-1b'
    }
}

ELB_CONFIG = {
    'mame': 'my-load-balancer',
    'service_name': 'elbv2',
    'cluster1': {
        't_group_name': 'cluster1',
        'PathPattern': '/cluster1*',
        'RulePriority': 1
    },
    'cluster2': {
        't_group_name': 'cluster2',
        'PathPattern': '/cluster1*',
        'RulePriority': 1
    }
}


IAM_CONFIG = {
    'service_name': 'iam',
    'role' : 'LabRole'
}


CODE_DEPLOY_CONFIG = {
    'service_name': 'codedeploy',
    'application_name' : 'lab1_app', 
    'github_repo_config' : {
        'repository': '',
        'commitId': ''  
    },
     'cluster1': {
        'dep_group_name': 'cluster1',
        'tag_filters': [
            {
                'Key': 'cluster',
                'Value': '1',
                'Type': 'KEY_AND_VALUE'
            },
        ]
    },
    'cluster2': {
        'dep_group_name': 'cluster2',
        'tag_filters': [
            {
                'Key': 'cluster',
                'Value': '2',
                'Type': 'KEY_AND_VALUE'
            },
        ]
    }
    

}

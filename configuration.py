REGION = 'us-east-1'
aws_access_key_id="ASIASRQQNEZNEEUCRCOK"
aws_secret_access_key="l6zAzceotvgLDhYidV4taatiPOTihn9xtuLf9S5L"
aws_session_token="FwoGZXIvYXdzEFoaDLh8+kQWF1Nam1DSFiLPAZafvHUSyMxgwNtW7fM3R/ejWN6MceJZ1CIzM48jD+nk7uixxaDxAj0Xfiw6EpKS2F4v2pCuaKjmjNZtliBJtkzDE/9eNBOrneeAr30LLH2PzVuuY2Tql8R5/6WklyKyJsRSLsaf8t5serzCVNJnsjivbttem5R5Jr+Pnwwi9Lz8nVrKiACTt7i2lutaOvouOzhnmqGwrEv/NUI2XfiSABMBxt3jwwj/iyL+XB7Q79es55qQbJSVpoKLZhfZ9PBKWSpjyICINgkg+KPFUgavyijsg/ioBjItPFCb7aFpwU8uF+abGBXJiVuq8otqz0RKkMQUj7miZcz++whHur1wquLm63xT"


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
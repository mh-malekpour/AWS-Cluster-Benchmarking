def get_vpc(ec2):
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    return vpc_id    

def create_key_pair(ec2, key_name):
    with open('my_keypair.pem', 'w') as file:
        key_pair = ec2.create_key_pair(KeyName=key_name, KeyType='rsa', KeyFormat='pem')
        file.write(key_pair.get('KeyMaterial'))
    key_pair_id = key_pair.get('KeyPairId')
    return key_pair_id

def create_security_group(ec2, vpc_id, group_name):
    response = ec2.create_security_group(
            GroupName=group_name,
            Description='',
            VpcId=vpc_id
        )
    security_group_id = response['GroupId']
    return security_group_id
    
def set_security_group_rules(ec2, sec_group_id):
    ec2.authorize_security_group_ingress(
                GroupId=sec_group_id,
                IpPermissions=[
                    {'IpProtocol': 'tcp', 
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                ]
            )

def lunch_ec2_instance(ec2, image_id, instance_type, key_name, sec_group, zone, profile, tags):
    response = ec2.run_instances(
            ImageId=image_id,
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            KeyName=key_name,
            SecurityGroups=[sec_group],
            Placement={
                'AvailabilityZone': zone
            },
            TagSpecifications=tags,
            IamInstanceProfile={
                'Name': profile
            },
            MetadataOptions={
                'InstanceMetadataTags': 'enabled'
            }
        )
    ec2_instance_id = response['Instances'][0]['InstanceId']
    return ec2_instance_id

def create_vpc(ec2, cidr_block):
    # Ensure a VPC with the specified CIDR block exists. If it doesn't, create it.
    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'cidr', 'Values': [cidr_block]}])

    if vpcs and vpcs.get('Vpcs'):
        return vpcs['Vpcs'][0]['VpcId']
    else:
        vpc = ec2.create_vpc(CidrBlock=cidr_block)
        return vpc['Vpc']['VpcId']


def create_subnet(ec2, vpc_id, cidr_block, availability_zone):
    # Ensure a subnet with the specified CIDR block within the given VPC exists. If it doesn't, create it.
    subnets = ec2.describe_subnets(
        Filters=[{'Name': 'cidr-block', 'Values': [cidr_block]}, {'Name': 'vpc-id', 'Values': [vpc_id]}])

    if subnets and subnets.get('Subnets'):
        return subnets['Subnets'][0]['SubnetId']
    else:
        subnet_response = ec2.create_subnet(VpcId=vpc_id, CidrBlock=cidr_block, AvailabilityZone=availability_zone)
        return subnet_response['Subnet']['SubnetId']


def create_key_pair(ec2, key_name):
    with open('my_keypair.pem', 'w') as file:
        key_pair = ec2.create_key_pair(KeyName=key_name, KeyType='rsa', KeyFormat='pem')
        file.write(key_pair.get('KeyMaterial'))
    key_pair_id = key_pair.get('KeyPairId')
    return key_pair_id


def create_security_group(ec2, vpc_id, group_name):
    # Ensure a security group with the specified name exists within the given VPC. If it doesn't, create it.
    security_groups = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [group_name]}, {'Name': 'vpc-id', 'Values': [vpc_id]}])

    if security_groups and security_groups.get('SecurityGroups'):
        return security_groups['SecurityGroups'][0]['GroupId']
    else:
        response = ec2.create_security_group(
            GroupName=group_name,
            Description=f'{group_name} security group',
            VpcId=vpc_id
        )
        return response['GroupId']


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

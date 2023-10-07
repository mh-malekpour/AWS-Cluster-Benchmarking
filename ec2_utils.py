import time
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
    # Ensure a key pair with the specified name exists. If it doesn't, create it and save the private key."""
    try:
        key_pairs = ec2.describe_key_pairs(KeyNames=[key_name])
        if key_pairs and key_pairs.get('KeyPairs'):
            return key_pairs['KeyPairs'][0]['KeyName']
    except ec2.exceptions.ClientError as e:
        pass

    with open(f'{key_name}.pem', 'w') as file:
        key_pair = ec2.create_key_pair(KeyName=key_name, KeyType='rsa', KeyFormat='pem')
        file.write(key_pair.get('KeyMaterial'))
    return key_pair.get('KeyName')


def create_security_group(ec2, vpc_id, group_name):
    # Ensure a security group with the specified name exists, If it doesn't, create it. Then setting up rules.
    security_groups = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [group_name]}, {'Name': 'vpc-id', 'Values': [vpc_id]}])

    if security_groups and security_groups.get('SecurityGroups'):
        return security_groups['SecurityGroups'][0]['GroupId']
    else:
        response = ec2.create_security_group(
            GroupName=group_name,
            Description=f'{group_name} security group',
            VpcId=vpc_id
        )
        # Setting up rules
        ec2.authorize_security_group_ingress(
            GroupId=response['GroupId'],
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                 },
            ]
        )
        return response['GroupId']


def get_latest_amazon_linux_2_image_id(ec2):
    # Filter for Amazon Linux 2 AMIs
    filters = [
        {
            'Name': 'name',
            'Values': ['amzn2-ami-hvm-*']
        },
        {
            'Name': 'architecture',
            'Values': ['x86_64']
        },
        {
            'Name': 'root-device-type',
            'Values': ['ebs']
        },
        {
            'Name': 'virtualization-type',
            'Values': ['hvm']
        },
        {
            'Name': 'image-type',
            'Values': ['machine']
        }
    ]

    # Describe images and get the latest one
    response = ec2.describe_images(Owners=['amazon'], Filters=filters)

    # Sort images by creation date
    images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)

    # Return the latest image's ID
    if images:
        return images[0]['ImageId']
    else:
        return None


def lunch_ec2_instance(ec2, image_id, instance_type, key_name, sec_group_ids, zone, profile, subnet_id, tags):
    response = ec2.run_instances(
        ImageId=image_id,
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[sec_group_ids],
        Placement={
            'AvailabilityZone': zone
        },
        TagSpecifications=tags,
        IamInstanceProfile={
            'Name': profile
        },
        MetadataOptions={
            'InstanceMetadataTags': 'enabled'
        },
        SubnetId=subnet_id
    )
    ec2_instance_id = response['Instances'][0]['InstanceId']
    return ec2_instance_id


def wait_instances_lunch(ec2, instances_ids):
    waiter = ec2.get_waiter('instance_status_ok')
    for instance_id in instances_ids:
        try:
            waiter.wait(
                    InstanceIds=[instance_id],
                    WaiterConfig={'Delay': 10}  
            )
        except Exception as e:
            time.sleep(300)




def get_subnet_ids(ec2, vpc_id, availability_zone):
    response = ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [vpc_id],
                },
                {
                    'Name': 'availability-zone',
                    'Values': availability_zone,
                }
            ]
        )
   
    subnet_ids = [subnet['SubnetId'] for subnet in response['Subnets']]
    return subnet_ids
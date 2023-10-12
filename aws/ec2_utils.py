"""
Utils  file for EC2 
"""

import time
def create_vpc(ec2, cidr_block):
    """
    It creates the vpc and returns the vpc_id
    """
    # Ensure a VPC with the specified CIDR block exists. If it doesn't, create it.
    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'cidr', 'Values': [cidr_block]}])

    if vpcs and vpcs.get('Vpcs'):
        vpc_id =  vpcs['Vpcs'][0]['VpcId']
    else:
        vpc = ec2.create_vpc(CidrBlock=cidr_block)
        vpc_id =  vpc['Vpc']['VpcId']
    print(f'VPC created {vpc_id}')
    return vpc_id

def create_subnet(ec2, vpc_id, cidr_block, availability_zone):
    """
    It creates the subnet
    """
    # Ensure a subnet with the specified CIDR block within the given VPC exists. If it doesn't, create it.
    subnets = ec2.describe_subnets(
        Filters=[
            {'Name': 'cidr-block', 'Values': [cidr_block]}, 
            {'Name': 'vpc-id', 'Values': [vpc_id]}, 
])

    for subnet in subnets.get('Subnets', []):
        if subnet['AvailabilityZone'] == availability_zone:
            subnet_id = subnet['SubnetId']
            print(f'Subnet id created {subnet_id}') 
            return subnet_id

    
    subnet_response = ec2.create_subnet(VpcId=vpc_id, CidrBlock=cidr_block, AvailabilityZone=availability_zone)
    subnet_id =  subnet_response['Subnet']['SubnetId']
    print(f'Subnet id created {subnet_id}')
    return subnet_id


def create_key_pair(ec2, key_name):
    """
    It creates the key pair
    """
    # Ensure a key pair with the specified name exists. If it doesn't, create it and save the private key."""
    try:
        key_pairs = ec2.describe_key_pairs(KeyNames=[key_name])
        if key_pairs and key_pairs.get('KeyPairs'):
            key_pair_id = key_pairs['KeyPairs'][0]['KeyName']
            print(f'Key pair created {key_pair_id}')
            return key_pair_id
    except ec2.exceptions.ClientError as e:
        pass

    with open(f'{key_name}.pem', 'w') as file:
        key_pair = ec2.create_key_pair(KeyName=key_name, KeyType='rsa', KeyFormat='pem')
        file.write(key_pair.get('KeyMaterial'))
        key_pair_id = key_pair.get('KeyName')
    print(f'Key pair created {key_pair_id}')
    return key_pair_id


def create_security_group(ec2, vpc_id, group_name):
    """
    it creates the security group
    """
    # Ensure a security group with the specified name exists, If it doesn't, create it. Then setting up rules.
    security_groups = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [group_name]}, {'Name': 'vpc-id', 'Values': [vpc_id]}])

    if security_groups and security_groups.get('SecurityGroups'):
        group_id =  security_groups['SecurityGroups'][0]['GroupId']
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
                {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            ]
        )
        group_id= response['GroupId']
    print(f'security group created {group_id}')
    return group_id


def get_latest_amazon_linux_2_image_id(ec2):
    """
    Retrives the imageid
    
    """
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
        image_id = images[0]['ImageId']
        print(f'Image retrieved {image_id}')
        return image_id
    else:
        return None


def lunch_ec2_instance(ec2, image_id, instance_type, key_name, sec_group_ids, zone, profile, subnet_id, tags):
    """
    It instatiates and lunches the ec2 instance
    """
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
        SubnetId=subnet_id, 
    )
    ec2_instance_id = response['Instances'][0]['InstanceId']
    print(f'Instance lunched {ec2_instance_id}')
    return ec2_instance_id


def wait_instances_lunch(ec2, instances_ids):
    """
    It waites for each instance id to be running and in an OK  status
    """
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
    """
    Gets the subnet ids given vpc and availability zone
    """
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


def attach_internet_gateway_to_vpc(ec2, vpc_id):
    """
    Attaches the internet gateway to the vc
    """
    response = ec2.describe_internet_gateways(
        Filters=[
            {'Name': 'attachment.vpc-id', 'Values': [vpc_id]}
        ]
    )
    if response['InternetGateways']:
        internet_gateway_id = response['InternetGateways'][0]['InternetGatewayId']
    else: 
        # Create an Internet Gateway
        response = ec2.create_internet_gateway()
        internet_gateway_id = response['InternetGateway']['InternetGatewayId']

        # Attach the Internet Gateway to the VPC
        ec2.attach_internet_gateway(
            InternetGatewayId=internet_gateway_id,
            VpcId=vpc_id
        )

        # Update route tables for subnets associated with the VPC
        route_table_ids = []

        # Describe the route tables associated with the VPC
        response = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        for route_table in response['RouteTables']:
            route_table_id = route_table['RouteTableId']
            route_table_ids.append(route_table_id)

        # Update route tables to route traffic through the Internet Gateway
        for route_table_id in route_table_ids:
            ec2.create_route(
                RouteTableId=route_table_id,
                DestinationCidrBlock='0.0.0.0/0',  # Route all traffic
                GatewayId=internet_gateway_id
            )
    print('Internet gateway attatched')
    return internet_gateway_id
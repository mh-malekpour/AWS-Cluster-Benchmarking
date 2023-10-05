import boto3

# Read AWS credentials from the text file
with open('aws_credentials.txt', 'r') as file:
    lines = file.readlines()
    aws_credentials = {}
    for line in lines:
        key, value = line.strip().split('=')
        aws_credentials[key] = value

# Initialize an AWS session using the credentials from the aws_credentials.txt file (put your aws credentials there)
session = boto3.Session(
    aws_access_key_id=aws_credentials['aws_access_key_id'],
    aws_secret_access_key=aws_credentials['aws_secret_access_key'],
    aws_session_token=aws_credentials.get('aws_session_token', None),
    region_name=aws_credentials.get('region_name', 'us-east-1')
)

# Initialize Boto3 clients for EC2, ELB, and Auto Scaling
ec2_client = session.client('ec2')
elbv2_client = session.client('elbv2')
autoscaling_client = session.client('autoscaling')

# Step 1: Create a VPC
vpc = ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
vpc_id = vpc['Vpc']['VpcId']

# Step 2: Create a Subnet (Added)
subnet_response = ec2_client.create_subnet(
    VpcId=vpc_id,
    CidrBlock='10.0.1.0/24',
    AvailabilityZone='us-east-1a'
)
subnet_id = subnet_response['Subnet']['SubnetId']

# Step 2: Create Security Groups
# Create a security group for m4.large instances
security_group_m4 = ec2_client.create_security_group(
    GroupName='M4SecurityGroup',
    Description='Security Group for m4.large instances',
    VpcId=vpc_id
)

# Configure inbound rules for security_group_m4 to allow necessary traffic
# Example:
ec2_client.authorize_security_group_ingress(
    GroupId=security_group_m4['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Adjust as needed
        },
        # Add more rules as required
    ]
)

# Create a security group for t2.large instances
security_group_t2 = ec2_client.create_security_group(
    GroupName='T2SecurityGroup',
    Description='Security Group for t2.large instances',
    VpcId=vpc_id
)

# Configure inbound rules for security_group_t2 to allow necessary traffic
# Example:
ec2_client.authorize_security_group_ingress(
    GroupId=security_group_t2['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Adjust as needed
        },
        # Add more rules as required
    ]
)

# Step 3: Create Key Pairs
# Create key pairs for SSH access to the instances
key_pair_m4 = ec2_client.create_key_pair(KeyName='M4KeyPair')
key_pair_t2 = ec2_client.create_key_pair(KeyName='T2KeyPair')

# Save the private keys to files for future use
with open('M4KeyPair.pem', 'w') as f:
    f.write(key_pair_m4['KeyMaterial'])

with open('T2KeyPair.pem', 'w') as f:
    f.write(key_pair_t2['KeyMaterial'])

# Step 4: Create Target Groups
# Create a target group for m4.large instances
target_group_m4 = elbv2_client.create_target_group(
    Name='M4TargetGroup',
    Protocol='HTTP',  # Adjust the protocol as needed
    Port=80,  # Specify the port your instances will listen on
    VpcId=vpc_id
)

# Optionally, configure health checks, routing policies, etc. for target_group_m4

# Create a target group for t2.large instances
target_group_t2 = elbv2_client.create_target_group(
    Name='T2TargetGroup',
    Protocol='HTTP',  # Adjust the protocol as needed
    Port=80,  # Specify the port your instances will listen on
    VpcId=vpc_id
)

# Optionally, configure health checks, routing policies, etc. for target_group_t2

# Step 5: Create Launch Configurations
# Create a launch configuration for m4.large instances
m4_launch_config_params = {
    'LaunchConfigurationName': 'M4LaunchConfig',
    'ImageId': 'ami-01ca3d6832d617907',  # Specify the AMI ID for m4.large instances
    'InstanceType': 'm4.large',
    'KeyName': 'M4KeyPair',  # Adjust the key pair name
    'SecurityGroups': [security_group_m4['GroupId']],
}

autoscaling_client.create_launch_configuration(**m4_launch_config_params)

# Create a launch configuration for t2.large instances
t2_launch_config_params = {
    'LaunchConfigurationName': 'T2LaunchConfig',
    'ImageId': 'ami-01ca3d6832d617907',  # Specify the AMI ID for t2.large instances
    'InstanceType': 't2.large',
    'KeyName': 'T2KeyPair',  # Adjust the key pair name
    'SecurityGroups': [security_group_t2['GroupId']],
}

autoscaling_client.create_launch_configuration(**t2_launch_config_params)

# Step 6: Get and List Subnets associated with the VPC (Removed)

# Step 7: Create Auto Scaling Groups for Clusters (Continued)
# Create an Auto Scaling Group for m4.large cluster
m4_asg_params = {
    'AutoScalingGroupName': 'M4ClusterASG',
    'LaunchConfigurationName': 'M4LaunchConfig',
    'MinSize': 5,
    'MaxSize': 5,
    'DesiredCapacity': 5,
    'VPCZoneIdentifier': subnet_id,  # Use the subnet ID created earlier
    'TargetGroupARNs': [target_group_m4['TargetGroups'][0]['TargetGroupArn']],
}

autoscaling_client.create_auto_scaling_group(**m4_asg_params)

# Create an Auto Scaling Group for t2.large cluster
t2_asg_params = {
    'AutoScalingGroupName': 'T2ClusterASG',
    'LaunchConfigurationName': 'T2LaunchConfig',
    'MinSize': 4,
    'MaxSize': 4,
    'DesiredCapacity': 4,
    'VPCZoneIdentifier': subnet_id,  # Use the subnet ID created earlier
    'TargetGroupARNs': [target_group_t2['TargetGroups'][0]['TargetGroupArn']],
}

autoscaling_client.create_auto_scaling_group(**t2_asg_params)

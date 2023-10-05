import argparse
import time
from configuration import EC2_CONFIG, ELB_CONFIG, IAM_CONFIG, TAGS, PROFILE
from configuration import REGION, aws_access_key_id, aws_secret_access_key, aws_session_token
from aws_service_utils import create_aws_service
from ec2_utils import get_vpc, create_security_group, set_security_group_rules, create_key_pair, lunch_ec2_instance
from elb_utils import create_target_group, register_targets 

parser = argparse.ArgumentParser()
parser.add_argument('--region', default=REGION, type=str)
parser.add_argument('--aws_access_key', default=aws_secret_access_key, type=str)
parser.add_argument('--aws_access_secret_token', default=aws_session_token, type=str)
parser.add_argument('--aws_key_id', default=aws_access_key_id, type=str)


if __name__ == "__main__":
    args = parser.parse_args()

    # step1 : create the aws services : ece2, elb, iam
    ec2 = create_aws_service(service=EC2_CONFIG['service_name'], 
                             region=args.region, 
                             secret_access_id=args.aws_key_id,
                             secret_access_key=args.aws_access_key, 
                             session_token=args.aws_access_secret_token
                                           )
    
    elb = create_aws_service(service= ELB_CONFIG['service_name'],                             
                             region=args.region, 
                             secret_access_id=args.aws_key_id,
                             secret_access_key=args.aws_access_key, 
                             session_token=args.aws_access_secret_token)
    
    iam = create_aws_service(IAM_CONFIG['service_name'],                             
                             region=args.region, 
                             secret_access_id=args.aws_key_id,
                             secret_access_key=args.aws_access_key, 
                             session_token=args.aws_access_secret_token)


    # step 2: create a security group and set ip rules
    vpc_id = get_vpc(ec2)
    # sec_group_id = create_security_group(ec2=ec2, vpc_id=vpc_id, group_name=EC2_CONFIG['security_group'])
    sec_group_id = "sg-0c224111622a5082f"
    # set_security_group_rules(ec2=ec2, sec_group_id=sec_group_id)
    # key_id = create_key_pair(ec2=ec2, key_name=EC2_CONFIG['key_pair'])
    key_id='key-0f03a7f9d35b36a00'

    # step 3: create instances and lunch 
    instances_cluster_1 = []
    instances_cluster_2 = []
    for i in range(4):
        tag = TAGS
        tag['Tags'][0]['Value']=str(1)
        tag['Tags'][1]['Value']=str(i)
        id_instance = lunch_ec2_instance(
            ec2=ec2, 
            image_id=EC2_CONFIG['image_id'],
            instance_type=EC2_CONFIG['clustor_1']['instance_type'], 
            key_name=EC2_CONFIG['key_pair'],
            sec_group=EC2_CONFIG['security_group'],
            zone= EC2_CONFIG['clustor_1']['availability_zone'], 
            profile=PROFILE,
            tags=[tag]
        )
        instances_cluster_1.append(id_instance)

    for i in range(4):
        tag = TAGS
        tag['Tags'][0]['Value']=str(2)
        tag['Tags'][1]['Value']=str(i)
        id_instance = lunch_ec2_instance(
            ec2=ec2, 
            image_id=EC2_CONFIG['image_id'],
            instance_type=EC2_CONFIG['clustor_2']['instance_type'], 
            key_name=EC2_CONFIG['key_pair'],
            sec_group=EC2_CONFIG['security_group'],
            zone= EC2_CONFIG['clustor_2']['availability_zone'], 
            profile=PROFILE,
            tags=[tag]
        )
        instances_cluster_2.append(id_instance)

    time.sleep(1000) # we need to wait for instances to be created

    # step4 : create target groups and assign instances so tht we can the can have clusters
    t_group_1 = create_target_group(elb, ELB_CONFIG['cluster1']['t_group_name'], vpc_id)
    t_group_2 = create_target_group(elb, ELB_CONFIG['cluster2']['t_group_name'], vpc_id)

    register_targets(elb=elb, t_group=t_group_1, instance_ids=instances_cluster_1)
    register_targets(elb=elb, t_group=t_group_2, instance_ids=instances_cluster_2)




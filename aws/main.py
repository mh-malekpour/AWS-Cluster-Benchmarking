import argparse
from configuration import EC2_CONFIG, ELB_CONFIG, IAM_CONFIG, TAGS, PROFILE, CODE_DEPLOY_CONFIG, IAM_CONFIG
from configuration import REGION, aws_access_key_id, aws_secret_access_key, aws_session_token
from aws_service_utils import create_aws_service
from ec2_utils import create_vpc, create_subnet, create_security_group, create_key_pair, \
    lunch_ec2_instance, wait_instances_lunch, get_subnet_ids, get_latest_amazon_linux_2_image_id, \
        attach_internet_gateway_to_vpc
from elb_utils import create_target_group, register_targets, create_app_lb, create_alb_listener, \
    create_alb_list_rule 
from ami_utils import get_role
from code_deploy_utils import create_application, create_deployment, create_deployment_group
from utils import save_aws_config


parser = argparse.ArgumentParser()
parser.add_argument('--region', default=REGION, type=str)
parser.add_argument('--aws_access_key', default=aws_secret_access_key, type=str)
parser.add_argument('--aws_access_secret_token', default=aws_session_token, type=str)
parser.add_argument('--aws_key_id', default=aws_access_key_id, type=str)

if __name__ == "__main__":
    aws_config= {}
    args = parser.parse_args()

    # step1 : create the aws services : ece2, elb, iam
    ec2 = create_aws_service(service=EC2_CONFIG['service_name'],
                             region=args.region,
                             secret_access_id=args.aws_key_id,
                             secret_access_key=args.aws_access_key,
                             session_token=args.aws_access_secret_token
                             )

    elb = create_aws_service(service=ELB_CONFIG['service_name'],
                             region=args.region,
                             secret_access_id=args.aws_key_id,
                             secret_access_key=args.aws_access_key,
                             session_token=args.aws_access_secret_token)

    iam = create_aws_service(IAM_CONFIG['service_name'],
                             region=args.region,
                             secret_access_id=args.aws_key_id,
                             secret_access_key=args.aws_access_key,
                             session_token=args.aws_access_secret_token)

    code_deploy = create_aws_service(CODE_DEPLOY_CONFIG['service_name'],
                             region=args.region,
                             secret_access_id=args.aws_key_id,
                             secret_access_key=args.aws_access_key,
                             session_token=args.aws_access_secret_token)

    # step 2: create vpc, subnet, security group and set ip rules
    vpc_id = create_vpc(ec2, cidr_block='10.0.0.0/16')
    aws_config['vpc_id'] = vpc_id
    sec_group_id = create_security_group(ec2=ec2, vpc_id=vpc_id, group_name=EC2_CONFIG['security_group'])
    aws_config['sec_group_id'] = sec_group_id
    key_id = create_key_pair(ec2=ec2, key_name=EC2_CONFIG['key_pair'])
    aws_config['key_id'] = key_id
    image_id = get_latest_amazon_linux_2_image_id(ec2=ec2)
    aws_config['image_id'] = image_id
    subnet_id1 = create_subnet(ec2, vpc_id, cidr_block='10.0.4.0/24', availability_zone='us-east-1a')
    subnet_id2 = create_subnet(ec2, vpc_id, cidr_block='10.0.3.0/24', availability_zone='us-east-1b')
    aws_config['subnet_id1'] = subnet_id1
    aws_config['subnet_id2'] = subnet_id2
    attach_internet_gateway_to_vpc(ec2, vpc_id) 

    # step 3: create instances and lunch 
    instances_cluster_1 = []
    instances_cluster_2 = []

    for i in range(4):
        tag = TAGS
        tag['Tags'][0]['Value'] = str(1)
        tag['Tags'][1]['Value'] = str(i)
        id_instance = lunch_ec2_instance(
            ec2=ec2,
            image_id=image_id,
            instance_type=EC2_CONFIG['cluster_1']['instance_type'],
            key_name=EC2_CONFIG['key_pair'],
            zone=EC2_CONFIG['cluster_1']['availability_zone'],
            profile=PROFILE,
            tags=[tag],
            sec_group_ids=sec_group_id,
            subnet_id=subnet_id1
        )
        instances_cluster_1.append(id_instance)

    for i in range(5):
        tag = TAGS
        tag['Tags'][0]['Value'] = str(2)
        tag['Tags'][1]['Value'] = str(i)
        id_instance = lunch_ec2_instance(
            ec2=ec2,
            image_id=image_id,
            instance_type=EC2_CONFIG['cluster_2']['instance_type'],
            key_name=EC2_CONFIG['key_pair'],
            zone=EC2_CONFIG['cluster_2']['availability_zone'],
            profile=PROFILE,
            tags=[tag],
            sec_group_ids=sec_group_id,
            subnet_id=subnet_id2
        )
        instances_cluster_2.append(id_instance)

    aws_config['instances_cluster_1'] = instances_cluster_1
    aws_config['instances_cluster_2'] = instances_cluster_2
    # wait untill all created intances are running
    wait_instances_lunch(ec2=ec2, instances_ids=instances_cluster_1)
    wait_instances_lunch(ec2=ec2, instances_ids=instances_cluster_2)
    

    # step4 : create target groups and assign instances so tht we can the can have clusters
    t_group_1 = create_target_group(elb, ELB_CONFIG['cluster1']['t_group_name'], vpc_id)
    t_group_2 = create_target_group(elb, ELB_CONFIG['cluster2']['t_group_name'], vpc_id)
    aws_config['t_group_1'] =t_group_1
    aws_config['t_group_2'] =t_group_2

    register_targets(elb=elb, t_group=t_group_1, instance_ids=instances_cluster_1)
    register_targets(elb=elb, t_group=t_group_2, instance_ids=instances_cluster_2)

    # step 5: instantiate application load balancer and configure it (listners, add routing roules)
    subnet_id = [subnet_id1, subnet_id2]
    alb_arn, alb_dns_name = create_app_lb(elb=elb,lb_name=ELB_CONFIG['name'], sec_group_ids=[sec_group_id], subnets=subnet_id)

    aws_config['subnet_id'] = subnet_id
    aws_config['alb_arn'] =alb_arn
    aws_config['alb_dns_name'] = alb_dns_name

    alb_listener_arn = create_alb_listener(elb, alb_arn, [t_group_1, t_group_2])
    aws_config['alb_listener_arn'] = alb_listener_arn
    alb_list_rule_1_arn = create_alb_list_rule(
            elb,
            alb_listener_arn,
            t_group_1,
            ELB_CONFIG['cluster1']['PathPattern'],
            ELB_CONFIG['cluster1']['RulePriority']
        )
    
    aws_config['alb_list_rule_1_arn'] = alb_list_rule_1_arn
    alb_list_rule_2_arn = create_alb_list_rule(
            elb,
            alb_listener_arn,
            t_group_1,
            ELB_CONFIG['cluster2']['PathPattern'],
            ELB_CONFIG['cluster2']['RulePriority']
    )
    aws_config['alb_list_rule_2_arn'] = alb_list_rule_2_arn

    
    # step 6: Flask application deployment: create application and deployment groyps
    role_arn = get_role(iam, IAM_CONFIG['role'])
    aws_config['role_arn'] = role_arn

    app_id = create_application(code_deploy=code_deploy, application_name=CODE_DEPLOY_CONFIG['application_name'])
    aws_config['app_id'] = app_id
    
    dep_group1= create_deployment_group(
        code_deploy=code_deploy, service_role_arn=role_arn, app_name=CODE_DEPLOY_CONFIG['application_name'], dep_group_name=CODE_DEPLOY_CONFIG['cluster1']['dep_group_name'], tag_filters= CODE_DEPLOY_CONFIG['cluster1']['tag_filters']
    )
    aws_config['dep_group1'] = dep_group1
    dep_group2 = create_deployment_group(
        code_deploy=code_deploy, service_role_arn=role_arn, app_name=CODE_DEPLOY_CONFIG['application_name'], dep_group_name=CODE_DEPLOY_CONFIG['cluster2']['dep_group_name'], tag_filters= CODE_DEPLOY_CONFIG['cluster2']['tag_filters']
    )
    aws_config['dep_group2'] = dep_group2


    # save aws configuration 
    save_aws_config(config=aws_config, save_file='aws_config.json')

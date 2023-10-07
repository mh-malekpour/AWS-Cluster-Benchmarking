"""
Utils file for ELB(Elastic load balancer servcie)
"""

def create_target_group(elb, t_group, vpc_id):
    """
    It creates the target group 
    """
    response = elb.create_target_group(
            Name=t_group,
            Protocol='HTTP',
            ProtocolVersion='HTTP1',
            Port=80,
            VpcId=vpc_id,
            HealthCheckProtocol='HTTP',
            TargetType='instance',
            IpAddressType='ipv4'
        )
    t_group = response['TargetGroups'][0]['TargetGroupArn']
    print(f'Target group created {t_group}')
    return t_group

def register_targets(elb, t_group, instance_ids):
    """
    It registers the instaces to the target groupm i.e. ceates the clusters
    """
    elb.register_targets(
            TargetGroupArn=t_group,
            Targets=[{'Id': ec2_instance_id, 'Port': 80} for ec2_instance_id in instance_ids]
        )


def create_app_lb(elb, lb_name, subnets, sec_group_ids):
    """
    It creates the application load balancer
    """
    response = elb.create_load_balancer(
            Name=lb_name,
            Subnets=subnets,
            SecurityGroups=sec_group_ids,
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )

    alb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    alb_dns_name = response['LoadBalancers'][0]['DNSName']
    return alb_arn, alb_dns_name



def create_alb_listener(elb, alb_arn, t_group_arns):
    """
    creates the alb_listener
    """
    response = elb.create_listener(
            LoadBalancerArn=alb_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'ForwardConfig': {
                        'TargetGroups': [
                            {
                                'TargetGroupArn': t_group_arns[0],
                                'Weight': 50
                            },
                            {
                                'TargetGroupArn': t_group_arns[1],
                                'Weight': 50
                            }
                        ]
                    }
                }
            ]
        )

    alb_listener_arn = response['Listeners'][0]['ListenerArn']
    print(f'ALB listener created {alb_listener_arn}')
    return alb_listener_arn


def create_alb_list_rule(elb, alb_listener_arn,target_group_arn,path_pattern,priority):
    """
    It creates the alb rule for the listner
    """
    response = elb.create_rule(
            ListenerArn=alb_listener_arn,
            Conditions=[
                {
                    'Field': 'path-pattern',
                    'Values': [
                        path_pattern
                    ]
                }
            ],
            Priority=priority,
            Actions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': target_group_arn
                }
            ]
        )

    alb_listener_rule_arn = response['Rules'][0]['RuleArn']
    return alb_listener_rule_arn

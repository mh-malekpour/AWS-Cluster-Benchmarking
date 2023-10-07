def create_target_group(elb, t_group, vpc_id):
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
    print(response)
    t_group = response['TargetGroups'][0]['TargetGroupArn']
    return t_group

def register_targets(elb, t_group, instance_ids):
    elb.register_targets(
            TargetGroupArn=t_group,
            Targets=[{'Id': ec2_instance_id, 'Port': 80} for ec2_instance_id in instance_ids]
        )


def create_app_lb(elb, lb_name, subnets, sec_group_ids):
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
        print(f'ALB listener created successfully.\n{alb_listener_arn}')
        return alb_listener_arn


def create_alb_list_rule(elb, alb_listener_arn,target_group_arn,path_pattern,priority):
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

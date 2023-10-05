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

    t_group = response['TargetGroups'][0]['TargetGroupArn']
    return t_group

def register_targets(elb, t_group, instance_ids):
    elb.register_targets(
            TargetGroupArn=t_group,
            Targets=[{'Id': ec2_instance_id, 'Port': 80} for ec2_instance_id in instance_ids]
        )


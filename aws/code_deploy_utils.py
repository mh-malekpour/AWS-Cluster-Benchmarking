"""
Code deply service utils
"""

def create_application(code_deploy, application_name):
    """
    Given the code deploy service, and the application name it creates the application and returns its id
    """
    response = code_deploy.list_applications()
    if application_name in response['applications']:
        application_info = code_deploy.get_application(applicationName=application_name)
        application_id = application_info['application']['applicationId']
    else:

        response = code_deploy.create_application(
                applicationName=application_name,
                computePlatform='Server'
            )

        application_id = response['applicationId']
    print(f'Application created: {application_id}')
    return application_id


def create_deployment_group(code_deploy, service_role_arn, app_name, dep_group_name, tag_filters):
    """
    Given the code deploy service,the role, the application name, deployment group and the tag filters, it creates the deployment 
    group and returns the deployment group id
    """
    response = code_deploy.list_deployment_groups(applicationName=app_name)
    if dep_group_name in response['deploymentGroups']:
        deployment_group_info = code_deploy.get_deployment_group(applicationName=app_name, deploymentGroupName=dep_group_name)
        deployment_group_id = deployment_group_info['deploymentGroupInfo']['deploymentGroupId']
    else:
        response = code_deploy.create_deployment_group(
                applicationName=app_name,
                deploymentGroupName=dep_group_name,
                deploymentConfigName='CodeDeployDefault.OneAtATime',
                ec2TagFilters=tag_filters,
                serviceRoleArn=service_role_arn,

                autoRollbackConfiguration={
                    'enabled': True,
                    'events': ['DEPLOYMENT_FAILURE']
                },

                deploymentStyle= {
                    'deploymentType': 'IN_PLACE',
                    'deploymentOption': 'WITHOUT_TRAFFIC_CONTROL'
                    }
            )

        deployment_group_id = response['deploymentGroupId']
    print(f'Deploymenet group created {deployment_group_id}')
    return deployment_group_id



def create_deployment(code_deploy, bucket, revision, deploy_group_name, app_name):
    revision['s3Location']['bucket'] = bucket
    response = code_deploy.create_deployment(
            description=f'Deploy flask server to {deploy_group_name}',
            applicationName=app_name,
            deploymentGroupName=deploy_group_name,
            revision=revision
        )
    deployment_id = response['deploymentId']
    print(f'Application deployment launched {deployment_id}')
    return deployment_id

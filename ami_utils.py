"""
Utils for IAM service
"""


def get_role(iam, role_name):
    """
    Gets the role_arn given the role name and the IAM service
    """
    response = iam.get_role(RoleName=role_name)
    role_arn = response['Role']['Arn']
    print(f'Role: {role_arn}')
    return role_arn

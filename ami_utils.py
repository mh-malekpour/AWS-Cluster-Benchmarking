import sys

def get_role(iam, role_name: str) -> str:
    try:
        response = iam.get_role(RoleName=role_name)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        role_arn = response['Role']['Arn']
        return role_arn

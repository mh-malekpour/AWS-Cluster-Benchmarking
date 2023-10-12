def get_aws_user_account(sts):
    response = sts.get_caller_identity()
    aws_user_account = response['Account']
    print(f'AWS account : {aws_user_account}')
    return aws_user_account

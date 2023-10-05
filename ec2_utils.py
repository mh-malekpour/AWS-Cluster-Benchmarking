import sys

def create_key_pair(ec2, key_name):
    try:
        with open('my_keypair.pem', 'w') as file:
            key_pair = ec2.create_key_pair(KeyName=key_name, KeyType='rsa', KeyFormat='pem')
            file.write(key_pair.get('KeyMaterial'))
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        key_pair_id = key_pair.get('KeyPairId')
        return key_pair_id

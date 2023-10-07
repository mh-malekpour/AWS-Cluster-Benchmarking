import json
def save_aws_config(config, save_file):
    """
    Save AWS config to a json file
    """
    with open(save_file, 'w') as file:
        json.dump(config, file)


def load_aws_config(config_file):
    """
    Load AWS config from json file
    """
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config
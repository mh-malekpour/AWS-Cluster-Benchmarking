# AWS-Cluster-Benchmarking
Cluster Benchmarking using EC2 Virtual Machines and Elastic Load Balancer (ELB)

## Project Environment Setup
```bash
# 1. Clone Repository:
git clone https://github.com/your-username/AWS-Cluster-Benchmarking.git

# 2. Navigate to Project Directory:
cd AWS-Cluster-Benchmarking

# 3. Install Pipenv:
pip install pipenv

# 4. Install Dependencies:
pipenv install --ignore-pipfile
```
You're now in the project's virtual environment, ready to run Python scripts and manage dependencies.

## Adding AWS Credentials

To use this project with AWS services:

1. **Create AWS Credentials File:**

   - Copy `aws_credentials_template.txt` and rename it to `aws_credentials.txt`.

2. **Edit `aws_credentials.txt`:**

   - Replace placeholders with your AWS credentials and region.
   - Do not commit this file to Git.

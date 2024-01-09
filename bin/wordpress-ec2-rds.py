#!/usr/bin/env python
import aws_cdk as cdk
from wordpress_ec2_rds.wordpress_ec2_rds_stack import WordpressEc2RdsStack  # Adjust the import path
from lib.config import config

app = cdk.App()

WordpressEc2RdsStack(
    app,
    'WordpressEc2RdsStack',
    env={'account': config['awsAccountNumber'], 'region': config['awsRegion']},  # Adjust to use account and region
    description=f'Deploys WordPress infrastructure with EC2 instances, RDS database, and uses S3 for storage. Stage: {config["stage"]}',
    tags={'Project': config['projectName'], 'Deployedby': config['deployedBy']}
)

app.synth()

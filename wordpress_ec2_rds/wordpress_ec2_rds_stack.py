

import aws_cdk as cdk
from aws_cdk import Stack
from constructs import Construct
from lib.constructs.vpc import CustomVPC
from lib.config import config
# from lib.constructs.rds import MySQLRdsInstance
# from lib.constructs.alb import WordpressApplicationLoadBalancer
# from lib.constructs.ec2 import WordpressAutoScalingGroup

class WordpressEc2RdsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC -- fetch the custom VPC
        custom_vpc_instance = CustomVPC(self, 'CustomVPC', {
            'prefix': config['project_name'],
            'vpc_cidr_block': '10.0.0.0/16',
        })

        # # Define properties for the MySQL RDS instance.
        # rds_props = {
        #     'vpc': custom_vpc_instance.vpc,  # VPC where the RDS instance will be deployed.
        #     'prefix': config['project_name'],  # Prefix for naming the RDS resources.
        #     'user': 'admin',  # Administrator username for the RDS instance.
        #     'database': 'wordpress',  # Database name to be created.
        #     'secret_name': f"{config['project_name']}/rds/mysql/credentials",  # Secret name for the RDS credentials.
        #     # Additional properties like port, instance size, etc., can be specified here.
        # }

        # # Create the MySQL RDS instance.
        # # This instance will be used by the WordPress application for its database needs.
        # mysql_rds_instance = MySQLRdsInstance(self, 'MySQLRdsInstance', rds_props)
        # # The RDS instance is now part of the stack and is integrated within the custom VPC.

        # Future constructs like EC2 instances, ALB, etc., will be added here in incremental updates.
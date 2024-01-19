

import aws_cdk as cdk
from aws_cdk import Stack
from constructs import Construct
from lib.constructs.vpc import CustomVPC
from lib.config import config
from lib.constructs.rds import MySQLRdsInstance
from lib.constructs.alb import WordpressApplicationLoadBalancer
from lib.constructs.ec2 import WordpressAutoScalingGroup

class WordpressEc2RdsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC -- fetch the custom VPC
        custom_vpc_instance = CustomVPC(self, 'CustomVPC', {
            'prefix': config['project_name'],
            'vpc_cidr_block': '10.0.0.0/16',
        })

        # # Define properties for the MySQL RDS instance
        rds_props = {
            'vpc': custom_vpc_instance.vpc,
            'prefix': config['project_name'],
            'user': 'admin',  # Admin username for the RDS instance
            'database': 'wordpress',  # Database name
            'secret_name': '/rds/mysql/credentials'  # Name of the secret in Secrets Manager
        }

        # # Instantiate the MySQL RDS instance
        mysql_rds_instance = MySQLRdsInstance(self, "MySQLRdsInstance", rds_props)
        # This will create an RDS instance and a proxy using the existing secret


        # Instantiate the WordpressAutoScalingGroup
        wordpress_asg = WordpressAutoScalingGroup(self, "WordpressAutoScalingGroup", 
            vpc= custom_vpc_instance.vpc,
            db_proxy_endpoint = mysql_rds_instance.rds_proxy.endpoint,  # RDS Proxy endpoint
            # ... other properties as needed
        )

        # Instantiate the WordpressApplicationLoadBalancer
        wordpress_alb = WordpressApplicationLoadBalancer(
            self, 
            "WordpressApplicationLoadBalancer", 
            props={
                'prefix': config['project_name'],
                'vpc': custom_vpc_instance.vpc,
                # Other properties as needed
            },
            auto_scaling_group=wordpress_asg.auto_scaling_group  # Pass the auto scaling group
        )


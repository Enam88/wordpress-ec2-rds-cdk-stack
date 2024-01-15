

import aws_cdk as cdk
from aws_cdk import Stack
from constructs import Construct
from lib.constructs.vpc import CustomVPC
from lib.config import config
from lib.constructs.rds import MySQLRdsInstance
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

        # Define properties for the MySQL RDS instance
        rds_props = {
            'vpc': custom_vpc_instance.vpc,
            'prefix': config['project_name'],
            'user': 'admin',  # Admin username for the RDS instance
            'database': 'wordpress',  # Database name
            'secret_name': '/rds/mysql/credentials'  # Name of the secret in Secrets Manager
        }

        # Instantiate the MySQL RDS instance
        mysql_rds_instance = MySQLRdsInstance(self, "MySQLRdsInstance", rds_props)
        # # This will create an RDS instance and a proxy using the existing secret


        # # Create the MySQL RDS instance.
        # # This instance will be used by the WordPress application for its database needs.
        # Instantiate the WordpressAutoScalingGroup construct
        # This will create an Auto Scaling Group with EC2 instances configured for WordPress
        # wordpress_asg = WordpressAutoScalingGroup(
        #     self,
        #     "WordpressAutoScalingGroup",
        #     vpc=custom_vpc_instance.vpc,  # Reference to the custom VPC
        #     db_secret_name=config['rds']['secret_name'],  # The name of the secret for RDS access
        #     wp_secret_name=config['wordpress']['secret_name'],  # The name of the secret for WordPress config
        #     rds_security_group=rds_instance.db_instance.connections.security_groups[0],  # The RDS instance's security group
        # )

        # # Output the Auto Scaling Group's security group ID for reference
        # cdk.CfnOutput(self, "WordpressASGSecurityGroup", value=wordpress_asg.security_group.security_group_id)

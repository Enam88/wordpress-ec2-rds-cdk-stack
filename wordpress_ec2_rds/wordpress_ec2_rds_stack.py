

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_ssm as ssm
from constructs import Construct
from lib.constructs.vpc import CustomVPC
from lib.config import config
from lib.constructs.rds import MySQLRdsInstance
# from lib.constructs.alb import WordpressApplicationLoadBalancer
from lib.constructs.ec2 import WordpressAutoScalingGroup

class WordpressEc2RdsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Fetch the custom VPC
        custom_vpc_instance = CustomVPC(self, 'CustomVPC', {
            'prefix': config['project_name'],
            'vpc_cidr_block': '10.0.0.0/16',
        })

        # Instantiate the WordpressAutoScalingGroup
        wordpress_asg = WordpressAutoScalingGroup(self, "WordpressAutoScalingGroup", vpc=custom_vpc_instance.vpc)

        # Define properties for the MySQL RDS instance
        rds_props = {
            'vpc': custom_vpc_instance.vpc,
            'prefix': config['project_name'],
            'secret_name': '/rds/mysql/credentials',  # Name of the secret in Secrets Manager
            'ec2_sg_id': wordpress_asg.security_group.security_group_id,  # EC2 security group ID
        }

        # Instantiate the MySQL RDS instance
        mysql_rds_instance = MySQLRdsInstance(self, "MySQLRdsInstance", rds_props)

        # Store the RDS Proxy Endpoint and Security Group ID in the Parameter Store
        ssm.StringParameter(self, "RdsProxyEndpointParameter",
                            parameter_name="/myapp/rds/proxy-endpoint",
                            string_value=mysql_rds_instance.rds_proxy.endpoint)

        ssm.StringParameter(self, "RdsProxySGIdParameter",
                            parameter_name="/myapp/rds/proxy-sg-id",
                            string_value=mysql_rds_instance.db_proxy_sg_id)
        
        
        # ... other constructs or resources if needed ...

        # # VPC -- fetch the custom VPC
        # custom_vpc_instance = CustomVPC(self, 'CustomVPC', {
        #     'prefix': config['project_name'],
        #     'vpc_cidr_block': '10.0.0.0/16',
        # })

        # # Define properties for the MySQL RDS instance
        # rds_props = {
        #     'vpc': custom_vpc_instance.vpc,
        #     'prefix': config['project_name'],
        #     'secret_name': '/rds/mysql/credentials',  # Name of the secret in Secrets Manager

        # }

        # # # Instantiate the MySQL RDS instance
        # mysql_rds_instance = MySQLRdsInstance(self, "MySQLRdsInstance", rds_props)
        # # This will create an RDS instance and a proxy using the existing secret


        # # # Instantiate the WordpressAutoScalingGroup
        # wordpress_asg = WordpressAutoScalingGroup(self, "WordpressAutoScalingGroup", 
        #     vpc= custom_vpc_instance.vpc,
        #     db_proxy_endpoint = mysql_rds_instance.rds_proxy.endpoint,  # RDS Proxy endpoint
        #     db_proxy_sg_id = mysql_rds_instance.db_proxy_sg_id,  # RDS Proxy Security Group ID           
        #       # ... other properties as needed
        # )

        #         # Update RDS properties with EC2 security group ID
        # # This is done after the instantiation of WordpressAutoScalingGroup
        # rds_props['ec2_sg_id'] = wordpress_asg.security_group.security_group_id


        # # Instantiate the WordpressApplicationLoadBalancer
        # wordpress_alb = WordpressApplicationLoadBalancer(
        #     self, 
        #     "WordpressApplicationLoadBalancer", 
        #     props={
        #         'prefix': config['project_name'],
        #         'vpc': custom_vpc_instance.vpc,
        #         # Other properties as needed
        #     },
        #     auto_scaling_group=wordpress_asg.auto_scaling_group  # Pass the auto scaling group
        # )


# # rds.py
# import aws_cdk as cdk
# from aws_cdk import aws_ec2 as ec2
# from aws_cdk import aws_rds as rds
# from aws_cdk import aws_secretsmanager as secretsmanager
# from constructs import Construct
# # from lib.constructs.vpc import CustomVPC
# import json

# class MySQLRdsInstance(Construct):
#     def __init__(self, scope: Construct, id: str, props: dict) -> None:
#         super().__init__(scope, id)

#         # Using the custom VPC from properties for network integration
#         custom_vpc = props['vpc']

#         # Create a security group for the RDS instance within the VPC
#         # This security group controls the inbound and outbound traffic to the RDS instance
#         rds_security_group = ec2.SecurityGroup(
#             self,
#             f"{props['prefix']}-rds-sg",
#             vpc=custom_vpc,
#             description="Security group for RDS instance"
#             # security_group_name=f"{props['prefix']}-rds-sg"
#         )

#         # Allow MySQL access (port 3306) from EC2 instances within the same VPC
#         # Assuming the EC2 instances' security group ID is passed in the properties
#         if 'ec2_sg_id' in props:
#             rds_security_group.add_ingress_rule(
#                 ec2.Peer.security_group_id(props['ec2_sg_id']),
#                 ec2.Port.tcp(3306),
#                 'Allow MySQL access from EC2 instances'
#             )

#         # Handle RDS credentials with AWS Secrets Manager
#         secret_name = props.get('secret_name', f"{props['prefix']}/rds/mysql/credentials")
#         self.db_secret = self.create_or_fetch_secret(secret_name, props)

#         # RDS Instance configuration
#         self.rds_instance = rds.DatabaseInstance(
#             self,
#             f"{props['prefix']}-MySqlRDSInstance",
#             credentials=rds.Credentials.from_secret(secret_name),
#             engine=rds.DatabaseInstanceEngine.mysql(
#                 version=rds.MysqlEngineVersion.VER_8_0_23),
#             instance_type=ec2.InstanceType.of(
#                 ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
#             vpc=custom_vpc,
#             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
#             security_groups=[rds_security_group],
#             storage_type=rds.StorageType.GP2,
#             allocated_storage=100,  # Configure as per requirement
#             backup_retention=cdk.Duration.days(7),
#             deletion_protection=False,  # Set to True for production environments
#             removal_policy=cdk.RemovalPolicy.DESTROY  # Consider changing for production
#         )

#         # Define the RDS Proxy
#         self.rds_proxy = rds.DatabaseProxy(
#             self,
#             f"{props['prefix']}-rds-proxy",
#             proxy_target=rds.ProxyTarget.from_instance(self.rds_instance),
#             secrets=[self.db_secret],
#             vpc=custom_vpc,
#             security_groups=[rds_security_group],
#             idle_client_timeout=cdk.Duration.minutes(10),
#             debug_logging=True,
#             require_tls=True,
#         )


#         # Expose RDS instance and secret attributes for access in other constructs
#         self.rds_instance = self.rds_instance
#         self.db_secret = secret_name
#         self.db_proxy = self.rds_proxy

#             # Continuing from the previous code...

#         # Define additional properties and configuration for the RDS instance
#         # ... [Additional RDS instance configuration]

#         # Method for creating or fetching a secret
#     def create_or_fetch_secret(self, secret_name: str, props: dict):
#         # Check if the secret exists and return it, else create a new secret
#         try:
#             existing_secret = secretsmanager.Secret.from_secret_name_v2(
#                 self, 'ExistingSecret', secret_name
#             )
#             return existing_secret
#         except Exception:
#             # Secret doesn't exist, create a new one
#             return secretsmanager.Secret(
#                 self, 'RDSInstanceSecret',
#                 secret_name=secret_name,
#                 generate_secret_string=secretsmanager.SecretStringGenerator(
#                     secret_string_template=json.dumps({
#                         'username': props['user'],
#                         'database': props['database'],
#                     }),

#                     generate_string_key='password',
#                     exclude_characters='{}[]()\'"/\\'
#                 ),)


# rds.py
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct

# Define the MySQLRdsInstance class
class MySQLRdsInstance(Construct):
    def __init__(self, scope: Construct, id: str, props: dict) -> None:
        super().__init__(scope, id)

        # Fetch the existing secret by its ARN
        self.db_secret = secretsmanager.Secret.from_secret_complete_arn(
            self, 
            "DbSecret", 
            "arn:aws:secretsmanager:eu-west-3:943240599753:secret:/rds/mysql/credentials-tg3CzL"
        )
        # Note: Replace the ARN with the actual ARN of your secret

                # Create a security group for the RDS instance within the VPC
        rds_security_group = ec2.SecurityGroup(
            self,
            f"{props['prefix']}-rds-sg",
            vpc=props['vpc'],  # Use the VPC provided in props
            description="Security group for RDS instance"
        )

        # Allow MySQL access (port 3306) from EC2 instances within the same VPC
        if 'ec2_sg_id' in props:
            rds_security_group.add_ingress_rule(
                ec2.Peer.security_group_id(props['ec2_sg_id']),
                ec2.Port.tcp(3306),
                'Allow MySQL access from EC2 instances'
            )
                # Create the RDS instance using the fetched secret for credentials
        self.rds_instance = rds.DatabaseInstance(
            self,
            f"{props['prefix']}-MySqlRDSInstance",
            credentials=rds.Credentials.from_secret(self.db_secret),
            engine=rds.DatabaseInstanceEngine.mysql(
            version=rds.MysqlEngineVersion.VER_8_0),
            instance_type=ec2.InstanceType.of(
            ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            vpc=props['vpc'],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            security_groups=[rds_security_group],
            storage_type=rds.StorageType.GP2,
            allocated_storage=20, # Specify desired storage size
            backup_retention=cdk.Duration.days(7),
            deletion_protection=False, # Consider setting to True for production
            removal_policy=cdk.RemovalPolicy.DESTROY # Adjust as needed
            )
        # Create an RDS Proxy for the RDS instance
        self.rds_proxy = rds.DatabaseProxy(
            self,
            f"{props['prefix']}-rds-proxy",
            proxy_target=rds.ProxyTarget.from_instance(self.rds_instance),
            vpc=props['vpc'],
            security_groups=[rds_security_group],
            idle_client_timeout=cdk.Duration.minutes(10),
            debug_logging=True,
            require_tls=True,
            secrets=[self.db_secret]  # Use the fetched secret here
        )

        # Expose RDS instance, secret, and proxy attributes for access in other constructs
        self.db_proxy_endpoint = self.rds_proxy.endpoint




    


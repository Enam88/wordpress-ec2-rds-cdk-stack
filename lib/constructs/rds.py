# rds.py
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct
import json

class MySQLRdsInstance(Construct):
    def __init__(self, scope: Construct, id: str, props: dict) -> None:
        super().__init__(scope, id)

        # Using the custom VPC from properties for network integration
        custom_vpc = props['vpc']

        # Create a security group for the RDS instance within the VPC
        # This security group controls the inbound and outbound traffic to the RDS instance
        rds_security_group = ec2.SecurityGroup(
            self,
            f"{props['prefix']}-rds-sg",
            vpc=custom_vpc,
            description="Security group for RDS instance"
            # security_group_name=f"{props['prefix']}-rds-sg"
        )

        # Allow MySQL access (port 3306) from EC2 instances within the same VPC
        # Assuming the EC2 instances' security group ID is passed in the properties
        if 'ec2_sg_id' in props:
            rds_security_group.add_ingress_rule(
                ec2.Peer.security_group_id(props['ec2_sg_id']),
                ec2.Port.tcp(3306),
                'Allow MySQL access from EC2 instances'
            )

        # Handle RDS credentials with AWS Secrets Manager
        secret_name = props.get('secret_name', f"{props['prefix']}/rds/mysql/credentials")
        secret = self.create_or_fetch_secret(secret_name, props)

        # RDS Instance configuration
        mysql_rds_instance = rds.DatabaseInstance(
            self,
            f"{props['prefix']}-MySqlRDSInstance",
            credentials=rds.Credentials.from_secret(secret),
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_23),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            vpc=custom_vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            security_groups=[rds_security_group],
            storage_type=rds.StorageType.GP2,
            allocated_storage=100,  # Configure as per requirement
            backup_retention=cdk.Duration.days(7),
            deletion_protection=False,  # Set to True for production environments
            removal_policy=cdk.RemovalPolicy.DESTROY  # Consider changing for production
        )

        # Expose RDS instance and secret attributes for access in other constructs
        self.rds_instance = mysql_rds_instance
        self.db_secret = secret

    def create_or_fetch_secret(self, secret_name: str, props: dict):
        """
        Create a new secret in Secrets Manager or fetch an existing one.
        This secret will store the RDS instance credentials.
        """
        try:
            # Attempt to fetch the existing secret
            return secretsmanager.Secret.from_secret_name_v2(
                self, 'ExistingSecret', secret_name
            )
        except Exception:
            # Secret doesn't exist, create a new one
            return secretsmanager.Secret(
                self, 'RDSInstanceSecret',
                secret_name=secret_name,
                generate_secret_string=secretsmanager.SecretStringGenerator(
                    secret_string_template=json.dumps({
                        'username': props['user'],
                        'database': props['database'],
                    }),
                    generate_string_key='password',
                    exclude_characters='{}[]()\'"/\\'  # Exclude characters that might cause issues
                ),
            )


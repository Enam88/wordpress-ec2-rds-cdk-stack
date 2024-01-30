
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
        db_secret = secretsmanager.Secret.from_secret_complete_arn(
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
            credentials=rds.Credentials.from_secret(db_secret),
            engine=rds.DatabaseInstanceEngine.mysql(
            version=rds.MysqlEngineVersion.VER_8_0),
            instance_type=ec2.InstanceType.of(
            ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            vpc=props['vpc'],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),  # Use the private subnets
            security_groups=[rds_security_group],
            storage_type=rds.StorageType.GP2,
            allocated_storage=20, # Specify desired storage size
            backup_retention=cdk.Duration.days(7),
            deletion_protection=False, # Consider setting to True for production
            removal_policy=cdk.RemovalPolicy.DESTROY,
            publicly_accessible=False # Adjust as needed
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
            secrets=[db_secret],
            # Use the fetched secret here
        )


        # Expose RDS instance, secret, and proxy attributes for access in other constructs
        self.db_proxy_endpoint = self.rds_proxy.endpoint

        # Expose the security group ID of the RDS Proxy
        self.db_proxy_sg_id = rds_security_group.security_group_id




    


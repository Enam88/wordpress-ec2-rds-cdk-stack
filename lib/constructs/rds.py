import json  # Add this import at the beginning of your file

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class MySQLRdsInstance(Construct):
    def __init__(self, scope: Construct, id: str, props: dict) -> None:
        super().__init__(scope, id)

        # use the vpc we exported from lib/constructs/vpc.py
        custom_vpc = props['vpc']

        # create the security group for RDS instance
        ingress_security_group = ec2.SecurityGroup(
            self,
            f"{props['prefix']}-rds-ingress",
            vpc=custom_vpc,
            security_group_name=f"{props['prefix']}-rds-ingress-sg"
        )

        ingress_security_group.add_ingress_rule(
            ec2.Peer.ipv4(custom_vpc.vpc_cidr_block),
            ec2.Port.tcp(props['port'] or 3306),
            'Allows only local resources inside VPC to access this MySQL port (default -- 3306)'
        )

        # Dynamically generate the username and password, then store in secrets manager
        database_credentials_secret = secretsmanager.Secret(
            self,
            f"{props['prefix']}-MySQLCredentialsSecret",
            secret_name=props['secretName'],
            description='Credentials to access Wordpress MYSQL Database on RDS',
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "' + props['user'] + '"}',
                exclude_punctuation=True,
                include_space=False,
                generate_string_key='password'
            )
        )

        # create RDS MySQL instance
        mysql_rds_instance = rds.DatabaseInstance(
            self,
            f"{props['prefix']}-MySqlRDSInstance",
            credentials=rds.Credentials.from_secret(database_credentials_secret),
            engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_5_7_31),
            port=props['port'],
            allocated_storage=100,
            storage_type=rds.StorageType.GP2,
            backup_retention=cdk.Duration.days(7),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T2,
                ec2.InstanceSize.MICRO
            ),
            vpc=custom_vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            removal_policy=cdk.RemovalPolicy.SNAPSHOT,
            deletion_protection=True,
            security_groups=[ingress_security_group]
        )

       # secrets for RDS instance
        self.secret_name = f"{props['prefix']}/rds/mysql/credentials"
        secretsmanager.Secret(self, 'RDSInstanceSecret', 
            secret_name=self.secret_name,
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({
                    'username': props['user'],
                    'database': props['database'],
                }),
                generate_string_key='password',
            ),
        )


        # make the secret name available for reference
        self.database_secret_name = database_credentials_secret.secret_name

        # Return the RDS instance
        self.mysql_rds_instance = mysql_rds_instance

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as secretsmanager
# from aws_cdk.aws_rds import DatabaseProxy as rdsproxy
from constructs import Construct
import json

class MySQLRdsInstance(Construct):
    def __init__(self, scope: Construct, id: str, props: dict) -> None:
        super().__init__(scope, id)

        custom_vpc = props['vpc']

        ingress_security_group = ec2.SecurityGroup(
            self,
            f"{props['prefix']}-rds-ingress",
            vpc=custom_vpc,
            security_group_name=f"{props['prefix']}-rds-ingress-sg"
        )

        ingress_security_group.add_ingress_rule(
            ec2.Peer.ipv4(custom_vpc.vpc_cidr_block),
            ec2.Port.tcp(props.get('port', 3306)),
            'Allows only local resources inside VPC to access this MySQL port (default -- 3306)'
        )

        # Check if the secret already exists by its name
        secret_name = props.get('secret_name', '/rds/mysql/credentials')  # Provide the existing secret name
        existing_secret = secretsmanager.Secret.from_secret_name_v2(self, 'ExistingSecret', secret_name)

        if not existing_secret:
            # Secret doesn't exist, create it
            secretsmanager.Secret(self, 'RDSInstanceSecret',
                secret_name=secret_name,
                generate_secret_string=secretsmanager.SecretStringGenerator(
                    secret_string_template=json.dumps({
                        'username': props['user'],
                        'database': props['database'],
                    }),
                    generate_string_key='password',
                ),
            )

        mysql_rds_instance = rds.DatabaseInstance(
            self,
            f"{props['prefix']}-MySqlRDSInstance",
            credentials=rds.Credentials.from_secret(existing_secret if existing_secret else secretsmanager.Secret.from_secret_name(self, 'RDSInstanceSecret', secret_name)),
            engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0),
            port=props.get('port', 3306),
            allocated_storage=100,
            storage_type=rds.StorageType.GP2,
            backup_retention=cdk.Duration.days(7),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T2,
                ec2.InstanceSize.MICRO
            ),
            vpc=custom_vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            deletion_protection=True,
            security_groups=[ingress_security_group]
        )

        # Create an RDS Proxy for the RDS instance
        rds_proxy = rds.DatabaseProxy(
            self,
            f"{props['prefix']}-RDSProxy",
            db_proxy_name=f"{props['prefix']}-RDSProxy",
            vpc=custom_vpc,
            secrets=[existing_secret if existing_secret else secretsmanager.Secret.from_secret_name(self, 'RDSInstanceSecret', secret_name)],
            debug_logging=False,  # Set to True for debug logging if needed
            proxy_target=rds.ProxyTarget.from_instance(mysql_rds_instance),
            require_tls=True,  # Enforce TLS encryption for connections
        )

        # Allow connections from the RDS Proxy to the RDS instance
        mysql_rds_instance.connections.allow_from(
            rds_proxy,
            ec2.Port.tcp(props.get('port', 3306)),
            "Allow connections from RDS Proxy",
        )

        self.database_secret_name = secret_name
        self.mysql_rds_instance = mysql_rds_instance


# import json

# import aws_cdk as cdk
# from aws_cdk import aws_ec2 as ec2
# from aws_cdk import aws_rds as rds
# from aws_cdk import aws_secretsmanager as secretsmanager
# from constructs import Construct
# from lib.constructs.sm import MySecretsManager  # Import your MySecretsManager construct

# class MySQLRdsInstance(Construct):
#     def __init__(self, scope: Construct, id: str, props: dict) -> None:
#         super().__init__(scope, id)

#         # use the vpc we exported from lib/constructs/vpc.py
#         custom_vpc = props['vpc']

#         # create the security group for RDS instance
#         ingress_security_group = ec2.SecurityGroup(
#             self,
#             f"{props['prefix']}-rds-ingress",
#             vpc=custom_vpc,
#             security_group_name=f"{props['prefix']}-rds-ingress-sg"
#         )

#         ingress_security_group.add_ingress_rule(
#             ec2.Peer.ipv4(custom_vpc.vpc_cidr_block),
#             ec2.Port.tcp(props['port'] or 3306),
#             'Allows only local resources inside VPC to access this MySQL port (default -- 3306)'
#         )

#         # Create MySecretsManager instance
#         sm_instance = MySecretsManager(self, 'MySecretsManager')

#         # secrets for RDS instance
#         self.secret_name = sm_instance.secret.secret_name

#         # create RDS MySQL instance
#         mysql_rds_instance = rds.DatabaseInstance(
#             self,
#             f"{props['prefix']}-MySqlRDSInstance",
#             credentials=rds.Credentials.from_secret(sm_instance.secret),
#             engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_5_7_31),
#             port=props['port'],
#             allocated_storage=100,
#             storage_type=rds.StorageType.GP2,
#             backup_retention=cdk.Duration.days(7),
#             instance_type=ec2.InstanceType.of(
#                 ec2.InstanceClass.T2,
#                 ec2.InstanceSize.MICRO
#             ),
#             vpc=custom_vpc,
#             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
#             removal_policy=cdk.RemovalPolicy.DESTROY,
#             deletion_protection=True,
#             security_groups=[ingress_security_group]
#         )

#         # Return the RDS instance
#         self.mysql_rds_instance = mysql_rds_instance


# import json  # Add this import at the beginning of your file

# import aws_cdk as cdk
# from aws_cdk import aws_ec2 as ec2
# from aws_cdk import aws_rds as rds
# from aws_cdk import aws_secretsmanager as secretsmanager
# from constructs import Construct


# class MySQLRdsInstance(Construct):
#     def __init__(self, scope: Construct, id: str, props: dict) -> None:
#         super().__init__(scope, id)

#         # use the vpc we exported from lib/constructs/vpc.py
#         custom_vpc = props['vpc']

#         # create the security group for RDS instance
#         ingress_security_group = ec2.SecurityGroup(
#             self,
#             f"{props['prefix']}-rds-ingress",
#             vpc=custom_vpc,
#             security_group_name=f"{props['prefix']}-rds-ingress-sg"
#         )

#         ingress_security_group.add_ingress_rule(
#             ec2.Peer.ipv4(custom_vpc.vpc_cidr_block),
#             ec2.Port.tcp(props['port'] or 3306),
#             'Allows only local resources inside VPC to access this MySQL port (default -- 3306)'
#         )

#         # Dynamically generate the username and password, then store in secrets manager
#         database_credentials_secret = secretsmanager.Secret(
#             self,
#             f"{props['prefix']}-MySQLCredentialsSecret",
#             secret_name=props['secretName'],
#             description='Credentials to access Wordpress MYSQL Database on RDS',
#             generate_secret_string=secretsmanager.SecretStringGenerator(
#                 secret_string_template='{"username": "' + props['user'] + '"}',
#                 exclude_punctuation=True,
#                 include_space=False,
#                 generate_string_key='password'
#             )
#         )

#         # create RDS MySQL instance
#         mysql_rds_instance = rds.DatabaseInstance(
#             self,
#             f"{props['prefix']}-MySqlRDSInstance",
#             credentials=rds.Credentials.username("enam"),
#             engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_5_7_31),
#             port=props['port'],
#             allocated_storage=100,
#             storage_type=rds.StorageType.GP2,
#             backup_retention=cdk.Duration.days(7),
#             instance_type=ec2.InstanceType.of(
#                 ec2.InstanceClass.T2,
#                 ec2.InstanceSize.MICRO
#             ),
#             vpc=custom_vpc,
#             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
#             removal_policy=cdk.RemovalPolicy.DESTROY,
#             deletion_protection=True,
#             security_groups=[ingress_security_group]
#         )

#        # secrets for RDS instance
#         self.secret_name = f"{props['prefix']}/rds/mysql/credentials"
#         secretsmanager.Secret(self, 'RDSInstanceSecret', 
#             secret_name=self.secret_name,
#             generate_secret_string=secretsmanager.SecretStringGenerator(
#                 secret_string_template=json.dumps({
#                     'username': props['user'],
#                     'database': props['database'],
#                 }),
#                 generate_string_key='password',
#             ),
#         )


#         # make the secret name available for reference
#         self.database_secret_name = database_credentials_secret.secret_name

#         # Return the RDS instance
#         self.mysql_rds_instance = mysql_rds_instance

# import json

# import aws_cdk as cdk
# from aws_cdk import aws_ec2 as ec2
# from aws_cdk import aws_rds as rds
# from constructs import Construct


# class MySQLRdsInstance(Construct):
#     def __init__(self, scope: Construct, id: str, props: dict) -> None:
#         super().__init__(scope, id)

#         # use the vpc we exported from lib/constructs/vpc.py
#         custom_vpc = props['vpc']

#         # create the security group for RDS instance
#         ingress_security_group = ec2.SecurityGroup(
#             self,
#             f"{props['prefix']}-rds-ingress",
#             vpc=custom_vpc,
#             security_group_name=f"{props['prefix']}-rds-ingress-sg"
#         )

#         ingress_security_group.add_ingress_rule(
#             ec2.Peer.ipv4(custom_vpc.vpc_cidr_block),
#             ec2.Port.tcp(props['port'] or 3306),
#             'Allows only local resources inside VPC to access this MySQL port (default -- 3306)'
#         )

#         # Directly specify the RDS credentials
#         database_credentials = {
#             'username': props['user'],
#             'password': props['password'],  # Set your desired password here
#         }

#         # create RDS MySQL instance
#         mysql_rds_instance = rds.DatabaseInstance(
#             self,
#             f"{props['prefix']}-MySqlRDSInstance",
#             credentials=rds.Credentials.from_username(props['user'], password=props['password']),
#             engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_5_7_31),
#             port=props['port'],
#             allocated_storage=100,
#             storage_type=rds.StorageType.GP2,
#             backup_retention=cdk.Duration.days(7),
#             instance_type=ec2.InstanceType.of(
#                 ec2.InstanceClass.T2,
#                 ec2.InstanceSize.MICRO
#             ),
#             vpc=custom_vpc,
#             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
#             removal_policy=cdk.RemovalPolicy.DESTROY,
#             deletion_protection=True,
#             security_groups=[ingress_security_group]
#         )

#         # Make credentials available for use in your WordPress configuration
#         self.database_credentials = database_credentials

#         # Return the RDS instance
#         self.mysql_rds_instance = mysql_rds_instance

# import aws_cdk as cdk
# from aws_cdk import aws_ec2 as ec2
# from aws_cdk import aws_rds as rds
# from constructs import Construct

# class MySQLRdsInstance(Construct):
#     def __init__(self, scope: Construct, id: str, props: dict) -> None:
#         super().__init__(scope, id)

#         # use the vpc we exported from lib/constructs/vpc.py
#         custom_vpc = props['vpc']

#         # create the security group for the RDS instance
#         ingress_security_group = ec2.SecurityGroup(
#             self,
#             f"{props['prefix']}-rds-ingress",
#             vpc=custom_vpc,
#             security_group_name=f"{props['prefix']}-rds-ingress-sg"
#         )

#         ingress_security_group.add_ingress_rule(
#             ec2.Peer.ipv4(custom_vpc.vpc_cidr_block),
#             ec2.Port.tcp(props['port'] or 3306),
#             'Allows only local resources inside VPC to access this MySQL port (default -- 3306)'
#         )

#         # create RDS MySQL instance
#         mysql_rds_instance = rds.DatabaseInstance(
#             self,
#             f"{props['prefix']}-MySqlRDSInstance",
#             credentials=rds.Credentials.from_username(
#                 props['user'],
#                 password=cdk.SecretValue.plain_text(props['password'])  # Use SecretValue for the password
#             ),
#             engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_5_7_31),
#             port=props['port'],
#             allocated_storage=100,
#             storage_type=rds.StorageType.GP2,
#             backup_retention=cdk.Duration.days(7),
#             instance_type=ec2.InstanceType.of(
#                 ec2.InstanceClass.T2,
#                 ec2.InstanceSize.MICRO
#             ),
#             vpc=custom_vpc,
#             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
#             removal_policy=cdk.RemovalPolicy.DESTROY,
#             deletion_protection=True,
#             security_groups=[ingress_security_group]
#         )

#         # Make credentials available for use in your WordPress configuration
#         self.database_credentials = {
#             'username': props['user'],
#             'password': props['password'],  # Still store the password in plain form for other use cases
#         }

#         # Return the RDS instance
#         self.mysql_rds_instance = mysql_rds_instance

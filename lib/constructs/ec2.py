# ec2.py
import aws_cdk as cdk

from aws_cdk import (
    aws_ec2 as ec2,
    aws_secretsmanager as secrets,
    aws_autoscaling as autoscaling,
    aws_iam as iam
)
from constructs import Construct

from lib.utils import replace_all_substrings
from lib.config import config

class WordpressAutoScalingGroup(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.IVpc, dns_name: str, db_secret_name: str, wp_secret_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Use the VPC we just created
        custom_vpc = vpc

        # Define a role for the WordPress instances
        role = iam.Role(
            self,
            f"{id}-instance-role",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ec2.amazonaws.com"),
                iam.ServicePrincipal("ssm.amazonaws.com"),
            ),
            managed_policies=[
                # Allows us to access instances via SSH using IAM and SSM
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                ),
                # Allows EC2 instance to access Secrets Manager and retrieve secrets
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "SecretsManagerReadWrite"
                ),
            ],
        )

        # Create a security group for the WordPress instance
        security_group = ec2.SecurityGroup(
            self,
            "wordpress-instances-sg",
            vpc=custom_vpc,
            allow_all_outbound=True,
            security_group_name="wordpress-instances-sg",
        )

        # Add an ingress rule to allow HTTP access from resources inside our VPC (like the ALB)
        security_group.add_ingress_rule(
            ec2.Peer.ipv4(custom_vpc.vpc_cidr_block),
            ec2.Port.tcp(80),
            "Allows HTTP access from resources inside our VPC (like the ALB)",
        )

        # Secrets for WP Admin
        secrets.Secret(
            self,
            "WordpressAdminSecrets",
            secret_name=wp_secret_name,
            description="Admin credentials to access WordPress",
            generate_secret_string=secrets.SecretStringGenerator(
                secret_string_template='{"username": "' + config["wordpress"]["admin"]["username"] + '", "email": "' + config["wordpress"]["admin"]["email"] + '"}',
                generate_string_key="password",
            ),
        )

# vpc.py
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from lib.config import config

class CustomVPC(Construct):
    def __init__(self, scope: Construct, id: str, props: dict) -> None:
        super().__init__(scope, id)

        # Accessing props from the config dictionary
        self.props = {
            'prefix': config['project_name'],
            'vpc_cidr_block': '10.0.0.0/16'  # Example CIDR block
        }


        # Create a VPC with public and isolated subnets
        self.vpc = ec2.Vpc(
            self,
            f"{self.props['prefix']}-vpc",
            max_azs=2,
            cidr=self.props['vpc_cidr_block'],
            enable_dns_hostnames=True,
            enable_dns_support=True,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{self.props['prefix']}-public",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PUBLIC, #FOR wp instance
                ),
                ec2.SubnetConfiguration(
                    name=f"{self.props['prefix']}-isolated",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED # for rds instance and its proxy
                ),
            ],
        )






        # Expose VPC ID, public and isolated subnets
        self.vpc_id = self.vpc.vpc_id
        self.public_subnets = self.vpc.public_subnets
        self.private_subnets = self.vpc.isolated_subnets




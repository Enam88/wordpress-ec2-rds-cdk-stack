# vpc.py
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from lib.config import config

class CustomVPC(Construct):
    def __init__(self, scope: Construct, id: str, props: dict) -> None:
        super().__init__(scope, id)

        # Creates a VPC with public and isolated subnets across multiple availability zones.
        self.vpc = ec2.Vpc(
            self,
            f"{props['prefix']}-vpc",
            max_azs=2,  # Supports high availability across 2 AZs.
            cidr=props['vpc_cidr_block'],
            enable_dns_hostnames=True,  # Facilitates the resolution of DNS hostnames.
            enable_dns_support=True,  # Ensures DNS resolution within the VPC.
            nat_gateways=0,  # No NAT gateways since there are no private subnets needing outbound access.
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{props['prefix']}-public",
                    cidr_mask=24,  # A /24 subnet allows for 256 IP addresses.
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    name=f"{props['prefix']}-isolated",
                    cidr_mask=24,  # Also a /24 subnet for isolated resources like RDS instances.
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            ],
        )

        # Exposes the VPC's ID and subnet details for other resources to reference.
        self.vpc_id = self.vpc.vpc_id
        self.public_subnets = self.vpc.public_subnets
        self.isolated_subnets = self.vpc.isolated_subnets

        # Security groups for both the public and isolated subnets are created to control traffic.
        self.public_security_group = self.create_security_group(
            f"{props['prefix']}-public-sg",
            "Security group for public subnets",
            self.vpc.public_subnets
        )

        self.isolated_security_group = self.create_security_group(
            f"{props['prefix']}-isolated-sg",
            "Security group for isolated subnets",
            self.vpc.isolated_subnets
        )

        # A security group specifically for RDS instances is created for tighter control.
        self.rds_security_group = self.create_security_group(
            f"{props['prefix']}-rds-sg",
            "Security group for RDS instances",
            self.vpc.isolated_subnets
        )

        # Allows MySQL traffic from the public security group to the RDS security group.
        self.rds_security_group.add_ingress_rule(
            self.public_security_group,
            ec2.Port.tcp(3306),
            "Allow MySQL access from EC2 instances"
        )

    def create_security_group(self, id: str, description: str, subnets):
        # Creates a security group with a descriptive name and description.
        sg = ec2.SecurityGroup(
            self,
            id,
            vpc=self.vpc,
            description=description,
            security_group_name=id
        )

        # Adds a rule to allow SSH access. For production, limit this to known IPs.
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH access")

        return sg

# Utilization of the CustomVPC construct in a stack.
custom_vpc = CustomVPC(
    scope=cdk.Stack(),
    id="CustomVPC",
    props={
        'prefix': config['project_name'],
        'vpc_cidr_block': '10.0.0.0/16',
    }
)

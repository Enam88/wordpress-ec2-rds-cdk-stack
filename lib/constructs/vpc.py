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
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{self.props['prefix']}-public",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    name=f"{self.props['prefix']}-isolated",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            ],
        )




        # Create and configure separate Network ACLs for public and private subnets
        self.public_nacl = self.create_nacl("public", self.props['prefix'])
        self.private_nacl = self.create_nacl("private", self.props['prefix'])

        # Associate NACLs with respective Subnets
        self.associate_nacl_with_subnets(self.vpc.public_subnets, self.public_nacl, "Public", self.props['prefix'])
        self.associate_nacl_with_subnets(self.vpc.isolated_subnets, self.private_nacl, "Private", self.props['prefix'])


    
    #create NetworkACL
    def create_nacl(self, subnet_type: str, prefix: str):
        nacl = ec2.NetworkAcl(
            self,
            f"{prefix}-{subnet_type}-nacl",
            vpc=self.vpc,
            network_acl_name=f"{prefix}-{subnet_type}-nacl"
        )
        # Define NACL rules based on subnet type
        if subnet_type == "public":
            self.add_standard_rules(nacl, "Inbound", ec2.TrafficDirection.INGRESS)
            self.add_standard_rules(nacl, "Outbound", ec2.TrafficDirection.EGRESS)
        elif subnet_type == "private":
            # Add private subnet specific rules here
            pass
        return nacl
    
    #function to associate nacl with subnets
    def associate_nacl_with_subnets(self, subnets, nacl, subnet_type, prefix):
        for subnet in subnets:
            ec2.SubnetNetworkAclAssociation(
                self,
                f"{prefix}-{subnet_type}SubnetAssociation{subnet.node.id}",
                network_acl=nacl,
                subnet=subnet
            )

            
    def add_standard_rules(self, nacl, rule_prefix: str, direction: ec2.TrafficDirection):
        base_rule_number = 100  # Starting rule number
        increment_step = 10     # Step to increment rule numbers

        # Ephemeral port range rule
        nacl.add_entry(
            f"{rule_prefix}Ephemeral",
            rule_number=base_rule_number,
            traffic=ec2.AclTraffic.tcp_port_range(1024, 65535),
            direction=direction,
            cidr=ec2.AclCidr.any_ipv4(),
            rule_action=ec2.Action.ALLOW
        )
        base_rule_number += increment_step  # Increment rule number

        # Specific port rules
        ports = {"HTTP": 80, "HTTPS": 443, "SSH": 22}
        for name, port in ports.items():
            nacl.add_entry(
                f"{rule_prefix}{name}",
                rule_number=base_rule_number,
                traffic=ec2.AclTraffic.tcp_port(port),
                direction=direction,
                cidr=ec2.AclCidr.any_ipv4(),
                rule_action=ec2.Action.ALLOW
            )
            base_rule_number += increment_step  # Increment rule number for next entry



        # Expose VPC ID, public and isolated subnets
        self.vpc_id = self.vpc.vpc_id
        self.public_subnets = self.vpc.public_subnets
        self.private_subnets = self.vpc.isolated_subnets




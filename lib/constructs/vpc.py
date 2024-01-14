# vpc.py
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from lib.config import config

class CustomVPC(Construct):
    def __init__(self, scope: Construct, id: str, props: dict) -> None:
        super().__init__(scope, id)

        # Create a VPC with specified CIDR block and subnet configurations
        self.vpc = ec2.Vpc(
            self,
            f"{props['prefix']}-vpc",
            max_azs=2,  # Specifies the number of Availability Zones to use
            cidr=props['vpc_cidr_block'],  # CIDR block for the VPC
            enable_dns_hostnames=True,  # Enable DNS hostnames in the VPC
            enable_dns_support=True,  # Enable DNS support in the VPC
            nat_gateways=0,  # Number of NAT gateways in the VPC
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{props['prefix']}-public",
                    cidr_mask=22,  # Subnet mask for the public subnet
                    subnet_type=ec2.SubnetType.PUBLIC,  # Subnet type
                ),
                ec2.SubnetConfiguration(
                    name=f"{props['prefix']}-isolated",
                    cidr_mask=22, # Subnet mask for the isolated subnet
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED ),],) # Subnet type
            # Expose VPC attributes for access by other constructs
        self.vpc_id = self.vpc.vpc_id
        self.public_subnets = self.vpc.public_subnets
        self.isolated_subnets = self.vpc.isolated_subnets

        # Create a Network ACL for the VPC
        nacl = ec2.NetworkAcl(
            self,
            f"{props['prefix']}-nacl",
            vpc=self.vpc,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        # Inbound rules
        # Allow HTTP and HTTPS traffic from any IP address
        nacl.add_entry(
            f"{props['prefix']}-InboundHTTP",
            rule_number=100,
            traffic=ec2.AclTraffic.tcp_port(80),
            direction=ec2.TrafficDirection.INGRESS,
            cidr=ec2.AclCidr.any_ipv4(),
            rule_action=ec2.Action.ALLOW,
        )
        nacl.add_entry(
            f"{props['prefix']}-InboundHTTPS",
            rule_number=110,
            traffic=ec2.AclTraffic.tcp_port(443),
            direction=ec2.TrafficDirection.INGRESS,
            cidr=ec2.AclCidr.any_ipv4(),
            rule_action=ec2.Action.ALLOW,
        )

        # Outbound rules
        # Allow HTTP and HTTPS traffic to any IP address
        nacl.add_entry(
            f"{props['prefix']}-OutboundHTTP",
            rule_number=100,
            traffic=ec2.AclTraffic.tcp_port(80),
            direction=ec2.TrafficDirection.EGRESS,
            cidr=ec2.AclCidr.any_ipv4(),
            rule_action=ec2.Action.ALLOW,
        )
        nacl.add_entry(
            f"{props['prefix']}-OutboundHTTPS",
            rule_number=110,
            traffic=ec2.AclTraffic.tcp_port(443),
            direction=ec2.TrafficDirection.EGRESS,
            cidr=ec2.AclCidr.any_ipv4(),
            rule_action=ec2.Action.ALLOW,
        )

        # Associate the NACL with the public subnets
        # For Public Subnets
        for subnet in self.vpc.public_subnets:
            ec2.CfnSubnetNetworkAclAssociation(
                self,
                f"{props['prefix']}-PublicSubnetAssociation-{subnet.node.id}",
                subnet_id=subnet.subnet_id,
                network_acl_id=nacl.network_acl_id)

        # Create a Network ACL for the Isolated Subnets (for RDS)
        isolated_nacl = ec2.NetworkAcl(
            self,
            f"{props['prefix']}-isolated-nacl",
            vpc=self.vpc,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),)

        # Inbound rules for Isolated Subnets
        # Allow MySQL traffic from the EC2 instances
        isolated_nacl.add_entry(
            f"{props['prefix']}-InboundMySQL",
            rule_number=150,
            traffic=ec2.AclTraffic.tcp_port(3306),
            direction=ec2.TrafficDirection.INGRESS,
            cidr=ec2.AclCidr.ipv4('172.22.0.0/22'),  # Replace with your EC2 Subnet CIDR
            rule_action=ec2.Action.ALLOW,
        )

        # Outbound rules for Isolated Subnets
        # Allow MySQL traffic to the EC2 instances
        isolated_nacl.add_entry(
            f"{props['prefix']}-OutboundMySQL",
            rule_number=150,
            traffic=ec2.AclTraffic.tcp_port(3306),
            direction=ec2.TrafficDirection.EGRESS,
            cidr=ec2.AclCidr.ipv4('172.22.0.0/22'),  # Replace with your EC2 Subnet CIDR
            rule_action=ec2.Action.ALLOW,
        )

        # Associate the Isolated NACL with the isolated subnets
        # For Isolated Subnets
        for subnet in self.vpc.isolated_subnets:
            ec2.CfnSubnetNetworkAclAssociation(
                self,
                f"{props['prefix']}-IsolatedSubnetAssociation-{subnet.node.id}",
                subnet_id=subnet.subnet_id,
                network_acl_id=isolated_nacl.network_acl_id
            )

custom_vpc = CustomVPC(
scope=cdk.Stack(),
id="CustomVPC",
props={
'prefix': config['project_name'],
'vpc_cidr_block': '172.22.0.0/16',
})
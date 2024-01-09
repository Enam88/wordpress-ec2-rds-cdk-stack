import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from lib.config import config  # Import the config module
from constructs import Construct
# from aws_cdk import App, Stack                    # core constructs


class CustomVPC(Construct):
    def __init__(self, scope: Construct, id: str, props: dict) -> None:
        super().__init__(scope, id)


        

        self.vpc = ec2.Vpc(
            self,
            f"{props['prefix']}-vpc",
            max_azs=2,  # RDS requires at least 2 availability zones
            cidr=props['cidr'],  # the IP address block of the VPC, e.g., '172.22.0.0/16'
            enable_dns_hostnames=True,
            enable_dns_support=True,
            # expensive -- we don't need that yet (we have no PRIVATE subnets)
            nat_gateways=0,
            subnet_configuration=[
                # {
                #     'cidr_mask': 22,
                #     'name': f"{props['prefix']}-public-",
                #     'subnet_type': ec2.SubnetType.PUBLIC,  # for WP instance
                # },
                # {
                #     'cidr_mask': 22,
                #     'name': f"{props['prefix']}-isolated-",
                #     'subnet_type': ec2.SubnetType.PRIVATE_ISOLATED,  # for RDS DB
                # },
                    ec2.SubnetConfiguration(name=f"{props['prefix']}-public-", cidr_mask=22, subnet_type=ec2.SubnetType.PUBLIC),
                    # ec2.SubnetConfiguration(name="private", cidr_mask=24, subnet_type=ec2.SubnetType.PRIVATE)
                    ec2.SubnetConfiguration(name=f"{props['prefix']}-isolated-", cidr_mask=22, subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)
            ],
        )

# Assuming that config.projectName and config.cidr are available in the config module
custom_vpc = CustomVPC(
    scope= cdk.Stack(),  # Provide a valid scope, you can adjust it based on your actual application structure
    id="CustomVPC",
    props={
        'prefix': config['projectName'],
        'cidr': '172.22.0.0/16',
    }
)

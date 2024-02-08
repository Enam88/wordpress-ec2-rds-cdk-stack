# ec2.py
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_autoscaling as autoscaling
from constructs import Construct
from lib.config import config

class WordpressAutoScalingGroup(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        key_pair_name = "demo-keypair"
        # Define a role for the WordPress instances
        role = iam.Role(
            self,
            f"{id}-instance-role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMReadOnlyAccess"),  # Added policy

            ],
        )

        # Create a security group for the WordPress instances
        security_group = ec2.SecurityGroup(
            self,
            "wordpress-instances-sg",
            vpc=vpc,
            allow_all_outbound=True,
        )

        # Allow HTTP, HTTPS, and SSH access from anywhere
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP access from anywhere")
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "Allow HTTPS access from anywhere")
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH access")

        with open(".\lib\scripts\wordpress_install.sh", 'r') as user_data_file:
            user_data_script = user_data_file.read()

        # Create an Auto Scaling Group for WordPress instances
        asg = autoscaling.AutoScalingGroup(
            self,
            "WordpressAutoScalingGroup",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            role=role,
            security_group=security_group,
            key_name=key_pair_name,
            user_data=ec2.UserData.custom(user_data_script),
            min_capacity=1,
            max_capacity=2,
            desired_capacity=1,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            associate_public_ip_address=True,
        )

        asg.scale_on_cpu_utilization("CpuScaling", target_utilization_percent=70)


        # Expose the security group and auto scaling group
        self.security_group = security_group
        self.auto_scaling_group = asg


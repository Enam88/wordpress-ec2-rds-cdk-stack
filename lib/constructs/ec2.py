# ec2.py
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_autoscaling as autoscaling
from constructs import Construct
from lib.config import config  # Importing your config

# Define the WordpressAutoScalingGroup class
class WordpressAutoScalingGroup(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.IVpc, db_proxy_endpoint: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

                # Define a role for the WordPress instances
        role = iam.Role(
            self,
            f"{id}-instance-role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite"),
            ],
        )

        # Create a security group for the WordPress instances
        security_group = ec2.SecurityGroup(
            self,
            "wordpress-instances-sg",
            vpc=vpc,
            allow_all_outbound=True,
        )

        # Allow HTTP and HTTPS access from anywhere
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP access from anywhere")
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "Allow HTTPS access from anywhere")

        # Prepare user data script for WordPress setup
        user_data_script = f"""#!/bin/bash
            # Install necessary packages
            yum -y update
            amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2
            yum install -y httpd mariadb-server

            # PHP7 installation for WordPress
            amazon-linux-extras enable php7.4
            yum install -y php7.4

            # Start the Apache server
            systemctl start httpd.service
            systemctl enable httpd.service

            # Install WordPress CLI
            curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
            chmod +x wp-cli.phar
            mv wp-cli.phar /usr/local/bin/wp

            # Wait for Secrets Manager to have RDS and WP secrets ready
            for i in {{1..30}}; do
                if aws secretsmanager get-secret-value --secret-id {config['wordpress']['secrets']['db_secrets_path']} && \
                aws secretsmanager get-secret-value --secret-id {config['wordpress']['secrets']['wp_secrets_path']}; then
                break
                fi
                sleep 10s
            done

            # Fetch and execute the WordPress installation script
            curl -s https://your-script-hosting-location/wordpress_installation.sh | bash
        """

                # Create an Auto Scaling Group for WordPress instances
        asg = autoscaling.AutoScalingGroup(
            self,
            "WordpressAutoScalingGroup",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
                machine_image=ec2.AmazonLinuxImage(),
                role=role,
                security_group=security_group,
                user_data=ec2.UserData.custom(user_data_script),
                min_capacity=1,
                max_capacity=2,
                desired_capacity=1,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                # Additional configurations as needed
                )
        
        # Expose the security group and auto scaling group
        self.security_group = security_group
        self.auto_scaling_group = asg



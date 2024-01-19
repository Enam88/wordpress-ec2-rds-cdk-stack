


import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from constructs import Construct

class WordpressApplicationLoadBalancer(Construct):
    def __init__(self, scope: Construct, id: str, props: dict, auto_scaling_group) -> None:
        super().__init__(scope, id)

        # Create a security group for the ALB that allows HTTP and HTTPS traffic
        alb_security_group = ec2.SecurityGroup(
            self,
            f"{props['prefix']}-ALBSecurityGroup",
            vpc=props['vpc'],
            description="Security Group for the Wordpress Application Load Balancer"
        )
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic from the internet"
        )
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "Allow HTTPS traffic from the internet"
        )

        # Create an Internet-Facing Application Load Balancer
        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            f"{props['prefix']}-ALB",
            vpc=props['vpc'],
            internet_facing=True,
            load_balancer_name=f"{props['prefix']}-alb",
            security_group=alb_security_group
        )

        # Create a target group for the ALB
        self.target_group = elbv2.ApplicationTargetGroup(
            self,
            f"{props['prefix']}-TargetGroup",
            vpc=props['vpc'],
            port=80,
            target_type=elbv2.TargetType.INSTANCE,
            health_check=elbv2.HealthCheck(
                interval=cdk.Duration.seconds(30),
                path="/",
                protocol=elbv2.Protocol.HTTP,
                timeout=cdk.Duration.seconds(5),
                healthy_threshold_count=2,
                unhealthy_threshold_count=5
            )
        )

        # Add a listener to the ALB
        self.listener = self.alb.add_listener(
            f"{props['prefix']}-Listener",
            port=80,
            default_target_groups=[self.target_group]
        )

        # Connect the ALB to the EC2 AutoScalingGroup
        self.target_group.add_target(auto_scaling_group)

        # Expose the DNS name of the load balancer
        self.load_balancer_dns_name = self.alb.load_balancer_dns_name

        # Output the DNS name of the ALB for easy reference
        cdk.CfnOutput(self, f"{props['prefix']}-ALB-DNS-Name", value=self.load_balancer_dns_name)


import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from constructs import Construct

class WordpressApplicationLoadBalancer(Construct):
    def __init__(self, scope: Construct, id: str, props: dict) -> None:
        super().__init__(scope, id)

        # Create an ALB
        alb = elbv2.ApplicationLoadBalancer(
            self,
            f"{props['prefix']}-alb",
            load_balancer_name=f"{props['prefix']}-alb",
            vpc=props['vpc'],
            internet_facing=True,
        )

        # Create a target group for the ALB to forward traffic to EC2 instances
        target_group = elbv2.ApplicationTargetGroup(
            self,
            f"{props['prefix']}-target-group",
            vpc=props['vpc'],
            port=80,  # Adjust the port as needed
            targets=[],  # You may add targets if needed
        )

        # Add the target group to the ALB listener
        alb_listener = alb.add_listener(
            f"{props['prefix']}-alb-listener",
            port=80,
            open=True,
            default_target_groups=[target_group],  # Add the target group
        )

        # Expose the DNS name of the load balancer
        self.load_balancer_dns_name = alb.load_balancer_dns_name

        # Print out the DNS name of the ALB
        cdk.CfnOutput(self, f"{props['prefix']}-alb-dns-name", value=alb.load_balancer_dns_name)



# import aws_cdk as cdk
# from aws_cdk import aws_ec2 as ec2
# from aws_cdk import aws_elasticloadbalancingv2 as elbv2
# from constructs import Construct


# class WordpressApplicationLoadBalancer(Construct):
#     def __init__(self, scope: Construct, id: str, props: dict) -> None:
#         super().__init__(scope, id)

#         # Create an ALB
#         alb = elbv2.ApplicationLoadBalancer(
#             self,
#             f"{props['prefix']}-alb",
#             load_balancer_name=f"{props['prefix']}-alb",
#             vpc=props['vpc'],
#             internet_facing=True,
#         )

#         # Create a target group for the ALB to forward traffic to EC2 instances
#         target_group = elbv2.ApplicationTargetGroup(
#             self,
#             f"{props['prefix']}-target-group",
#             vpc=props['vpc'],
#             port=80,  # Adjust the port as needed
#             targets=[],  # You may add targets if needed
#         )

#         # Add the target group to the ALB listener
#         alb_listener = alb.add_listener(
#             f"{props['prefix']}-alb-listener",
#             port=80,
#             open=True,
#             default_target_groups=[target_group],  # Add the target group
#         )

#         # Expose the DNS name of the load balancer
#         self.load_balancer_dns_name = alb.load_balancer_dns_name

#         # Print out the DNS name of the ALB
#         cdk.CfnOutput(self, f"{props['prefix']}-alb-dns-name", value=alb.load_balancer_dns_name)
        
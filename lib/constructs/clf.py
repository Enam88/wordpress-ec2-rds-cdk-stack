import aws_cdk as cdk
from aws_cdk import aws_cloudfront as cloudfront
from constructs import Construct

class CloudFrontStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, alb_dns_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create CloudFront distribution
        distribution = cloudfront.CloudFrontWebDistribution(self, 'CloudFrontDistribution',
            origin_configs=[
                cloudfront.SourceConfiguration(
                    custom_origin_source=cloudfront.CustomOriginConfig(
                        domain_name=alb_dns_name,  # ALB DNS name passed as a parameter
                        origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
                    ),
                    behaviors=[cloudfront.Behavior(is_default_behavior=True)]
                )
            ]
        )

        # Output the CloudFront distribution domain name
        cdk.CfnOutput(self, 'CloudFrontDistributionDomain', value=distribution.distribution_domain_name)



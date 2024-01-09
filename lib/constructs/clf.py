import aws_cdk as cdk
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from lib.config import config  # Import your project config module
from constructs import Construct


class CloudFrontStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Get the ALB DNS name from the config
        alb_dns_name = config['alb_dns_name']

        # Create an ACM certificate (replace with your actual certificate ARN)
        certificate_arn = 'arn:aws:acm:region:account-id:certificate/certificate-id'
        certificate = acm.Certificate.from_certificate_arn(self, 'Certificate', certificate_arn)

        # Create CloudFront distribution
        distribution = cloudfront.CloudFrontWebDistribution(self, 'CloudFrontDistribution',
            origin_configs=[
                cloudfront.SourceConfiguration(
                    custom_origin_source=cloudfront.CustomOriginConfig(
                        domain_name=alb_dns_name,
                        origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
                    ),
                    behaviors=[
                        cloudfront.Behavior(is_default_behavior=True),
                    ]
                )
            ],
            alias_configuration={
                'acm_cert_ref': certificate.certificate_arn,
                'names': [config['domain_name']],  # Replace with your domain name
            }
        )

        # Output the CloudFront distribution domain name
        cdk.CfnOutput(self, 'CloudFrontDistributionDomain', value=distribution.distribution_domain_name)

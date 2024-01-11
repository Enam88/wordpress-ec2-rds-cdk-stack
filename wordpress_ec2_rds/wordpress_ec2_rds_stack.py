# import aws_cdk as cdk
# # from aws_cdk import Stack
# from constructs import Construct
# from lib.constructs.vpc import CustomVPC
# from lib.config import config
# from lib.constructs.rds import MySQLRdsInstance
# from lib.constructs.sm import  MySecretsManager
# from lib.constructs.alb import WordpressApplicationLoadBalancer
# from lib.constructs.ec2 import WordpressAutoScalingGroup
# from aws_cdk import aws_cloudfront as cloudfront
# from aws_cdk import aws_iam as iam
# import json

# # ... (previous imports)

# class WordpressEc2RdsStack(Stack):
#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # VPC -- fetch the custom VPC
#         custom_vpc_instance = CustomVPC(self, 'CustomVPC', {
#             'prefix': config['projectName'],
#             'cidr': '172.22.0.0/16',
#         })

#         # RDS -- create the MySQL database
#         rds_instance = MySQLRdsInstance(self, 'MySQLRDSInstance', {
#             'prefix': config['projectName'],
#             'vpc': custom_vpc_instance.vpc,
#             'user': 'wordpress_admin',
#             'password': 'your_db_password',  # Set your desired password here
#             'database': 'awesome-wp-site-db',
#             'port': 3306,
#         })

#         # ALB -- for our single instance
#         alb_instance = WordpressApplicationLoadBalancer(self, 'WordpressALB', {
#             'prefix': config['projectName'],
#             'vpc': custom_vpc_instance.vpc,
#         })

#         # CloudFront distribution
#         cloudfront_distribution = cloudfront.CloudFrontWebDistribution(self, 'WordpressCloudFront',
#             origin_configs=[
#                 cloudfront.SourceConfiguration(
#                     custom_origin_source=cloudfront.CustomOriginConfig(
#                         domain_name=alb_instance.load_balancer_dns_name,
#                         origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
#                     ),
#                     behaviors=[cloudfront.Behavior(is_default_behavior=True)]
#                 ),
#             ],
#         )

#        # EC2 Auto Scaling Group
#         wordpress_asg = WordpressAutoScalingGroup(self, "WordpressASG", vpc=custom_vpc_instance.vpc,
#                                                 dns_name=cloudfront_distribution.distribution_domain_name,
#                                                 db_secret_name='',  # No need for secret_arn if not using Secrets Manager
#                                                 wp_secret_name=f"{config['projectName']}/WordpressAdminSecrets")

#         # Fetch the user script from the file system as a string
#         with open('lib/scripts/wordpress_install.sh', 'r') as file:
#             user_script = file.read()

#         # Replace the following variable substrings in the userScript
#         replace_dict = {
#             '_DB_SECRETS_PATH_': '',  # No need for secret_arn if not using Secrets Manager
#             '_WP_SECRETS_PATH_': f"{config['projectName']}/WordpressAdminSecrets",
#             '_AWS_REGION_': config['stack']['region'],
#             '_WP_DB_NAME_': config['wordpress']['site']['databaseName'],
#             '_WP_SITE_TITLE_': config['wordpress']['site']['title'],
#             '_WP_SITE_INSTALL_PATH_': config['wordpress']['site']['installPath'],
#             '_WP_SITE_BASE_DOMAIN_': alb_instance.load_balancer_dns_name,
#         }

#         modified_user_script = self.replace_all_substrings(replace_dict, user_script)

#         # Add a role that allows access to AWS Secrets Manager (Update this based on your requirements)
#         role = iam.Role(self, 'WordpressASGRole',
#                 assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["secretsmanager:GetSecretValue"],
#                 resources=[rds_instance.mysql_rds_instance.secret.secret_arn,
#                            f"{config['projectName']}/WordpressAdminSecrets"],
#             )
#         )

#         # Create and export out the autoscaling group
#         self.asg = wordpress_asg  # Use the modified WordpressAutoScalingGroup instance

#         cdk.CfnOutput(self, "ALBDnsName", value=alb_instance.load_balancer_dns_name)

#     @staticmethod
#     def replace_all_substrings(replace_dict, input_str):
#         for key, value in replace_dict.items():
#             input_str = input_str.replace(key, value)
#         return input_str




# import aws_cdk as cdk
# from aws_cdk import Stack
# from constructs import Construct
# from lib.constructs.vpc import CustomVPC
# from lib.config import config
# from lib.constructs.rds import MySQLRdsInstance
# from lib.constructs.alb import WordpressApplicationLoadBalancer
# from lib.constructs.ec2 import WordpressAutoScalingGroup
# from aws_cdk import aws_cloudfront as cloudfront
# from aws_cdk import aws_secretsmanager as secretsmanager
# from aws_cdk import aws_iam as iam
# import json

# class WordpressAutoScalingGroup(Construct):
#     def __init__(self, scope: Construct, id: str, vpc, dns_name, db_secret_name, wp_secret_name, **kwargs) -> None:
#         super().__init__(scope, id, **kwargs)

#         # Your existing code for auto scaling group

#         # Add the following property to fetch WordPress secret name
#         self._wp_secret_name = wp_secret_name

#     # Add the property getter for WordPress secret name
#     @property
#     def wp_secret_name(self) -> str:
#         return self._wp_secret_name


# class WordpressEc2RdsStack(Stack):

#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # VPC -- fetch the custom VPC
#         custom_vpc_instance = CustomVPC(self, 'CustomVPC', {
#             'prefix': config['projectName'],
#             'cidr': '172.22.0.0/16',
#         })

#         # RDS -- create the MySQL database
#         rds_instance = MySQLRdsInstance(self, 'MySQLRDSInstance', {
#             'prefix': config['projectName'],
#             'vpc': custom_vpc_instance.vpc,
#             'user': 'wordpress_admin',
#             'database': 'awesome-wp-site-db',
#             'port': 3306,
#             'secretName': f"{config['projectName']}/rds/mysql/credentials",
#         })

    #     # ALB -- for our single instance
    #     alb_instance = WordpressApplicationLoadBalancer(self, 'WordpressALB', {
    #         'prefix': config['projectName'],
    #         'vpc': custom_vpc_instance.vpc,
    #     })

    #     # CloudFront distribution
    #     cloudfront_distribution = cloudfront.CloudFrontWebDistribution(self, 'WordpressCloudFront',
    #         origin_configs=[
    #             cloudfront.SourceConfiguration(
    #                 custom_origin_source=cloudfront.CustomOriginConfig(
    #                     domain_name=alb_instance.load_balancer_dns_name,
    #                     origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
    #                 ),
    #                 behaviors=[cloudfront.Behavior(is_default_behavior=True)]
    #             ),
    #         ],
    #     )

    #     # EC2 Auto Scaling Group
    #     wordpress_asg = WordpressAutoScalingGroup(self, "WordpressASG", vpc=custom_vpc_instance.vpc,
    #                                               dns_name=cloudfront_distribution.distribution_domain_name,
    #                                               db_secret_name=rds_instance.secret_name,
    #                                               wp_secret_name=f"{config['projectName']}/WordpressAdminSecrets")

    #     # Secrets for WP Admin
    #     secretsmanager.Secret(self, 'WordpressAdminSecrets',
    #                         secret_name=wordpress_asg.wp_secret_name,
    #                         description='Admin credentials to access Wordpress',
    #                         generate_secret_string={
    #                             'secret_string_template': json.dumps({
    #                                 'username': config['wordpress']['admin']['username'],
    #                                 'email': config['wordpress']['admin']['email'],
    #                             }),
    #                             'generate_string_key': 'password',
    #                         })

    #     # Fetch the user script from the file system as a string
    #     with open('lib/scripts/wordpress_install.sh', 'r') as file:
    #         user_script = file.read()

    #     # Replace the following variable substrings in the userScript
    #     replace_dict = {
    #         '_DB_SECRETS_PATH_': rds_instance.secret_name,
    #         '_WP_SECRETS_PATH_': f"{config['projectName']}/WordpressAdminSecrets",
    #         '_AWS_REGION_': config['stack']['region'],
    #         '_WP_DB_NAME_': config['wordpress']['site']['databaseName'],
    #         '_WP_SITE_TITLE_': config['wordpress']['site']['title'],
    #         '_WP_SITE_INSTALL_PATH_': config['wordpress']['site']['installPath'],
    #         '_WP_SITE_BASE_DOMAIN_': alb_instance.load_balancer_dns_name,
    #     }

    #     modified_user_script = self.replace_all_substrings(replace_dict, user_script)

    #     # Add a role that allows access to AWS Secrets Manager
    #     role = iam.Role(self, 'WordpressASGRole',
    #                     assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))

    #     role.add_to_policy(
    #         iam.PolicyStatement(
    #             effect=iam.Effect.ALLOW,
    #             actions=["secretsmanager:GetSecretValue"],
    #             resources=[rds_instance.secret_name, f"{config['projectName']}/WordpressAdminSecrets"],
    #         )
    #     )

    #     # Create and export out the autoscaling group
    #     self.asg = wordpress_asg  # Use the modified WordpressAutoScalingGroup instance

    #     cdk.CfnOutput(self, "ALBDnsName", value=alb_instance.load_balancer_dns_name)

    # @staticmethod
    # def replace_all_substrings(replace_dict, input_str):
    #     for key, value in replace_dict.items():
    #         input_str = input_str.replace(key, value)
    #     return input_str




import aws_cdk as cdk
from aws_cdk import Stack
from constructs import Construct
from lib.constructs.vpc import CustomVPC
from lib.config import config
from lib.constructs.rds import MySQLRdsInstance
from lib.constructs.sm import MySecretsManager
# from lib.constructs.alb import WordpressApplicationLoadBalancer
# from lib.constructs.ec2 import WordpressAutoScalingGroup
# from aws_cdk import aws_cloudfront as cloudfront

# from aws_cdk import aws_secretsmanager as secretsmanager
# from aws_cdk import aws_iam as iam
# import json

class WordpressEc2RdsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC -- fetch the custom VPC
        custom_vpc_instance = CustomVPC(self, 'CustomVPC', {
            'prefix': config['projectName'],
            'vpc_cidr_block': '172.22.0.0/16',
        })

        # # Create Secrets Manager
        # sm_instance = MySecretsManager(self, 'MySecretsManager')


        # Create RDS instance
        rds_instance = MySQLRdsInstance(self, 'MySQLRDSInstance', {
            'prefix': config['projectName'],
            'vpc': custom_vpc_instance.vpc,
            'user': 'admin',
            'database': 'mydatabase',
            'port': 3306,  # Specify the port if needed
            'secret_arn': 'arn:aws:secretsmanager:eu-west-3:943240599753:secret:/rds/mysql/credentials-tg3CzL',
            'secret_name': '/rds/mysql/credentials',  # Specify the secret name if needed
        })
        
        # # Create a secret with an alias using your custom construct
        # wp_secrets_manager = MySecretsManager(self, 'WordpressSecretsManager')
        # wp_credentials_secret = wp_secrets_manager.secret

        # # RDS -- create the MySQL database
        # rds_instance = MySQLRdsInstance(self, 'MySQLRDSInstance', {
        #     'prefix': config['projectName'],
        #     'vpc': custom_vpc_instance.vpc,
        #     'user': 'wordpress_admin',
        #     'database': 'awesome-wp-site-db',
        #     'port': 3306,
        #     'secretName': f"{config['projectName']}/rds/mysql/credentials",
        # })

    #     # ALB -- for our single instance
    #     alb_instance = WordpressApplicationLoadBalancer(self, 'WordpressALB', {
    #         'prefix': config['projectName'],
    #         'vpc': custom_vpc_instance.vpc,
    #     })


    #     # CloudFront distribution
    #     cloudfront_distribution = cloudfront.CloudFrontWebDistribution(self, 'WordpressCloudFront',
    #         origin_configs=[
    #             cloudfront.SourceConfiguration(
    #                 custom_origin_source=cloudfront.CustomOriginConfig(
    #                     domain_name=alb_instance.load_balancer_dns_name,
    #                     origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
    #                 ),
    #                 behaviors=[cloudfront.Behavior(is_default_behavior=True)]
    #             ),
    #         ],
    #     )


    #     # EC2 Auto Scaling Group
    #     # wordpress_asg = WordpressAutoScalingGroup(self, "WordpressASG", vpc=custom_vpc_instance.vpc,
    #     #                                           dns_name=alb_instance.load_balancer_dns_name,
    #     #                                           db_secret_name=rds_instance.secret_name,
    #     #                                           wp_secret_name=f"{config['projectName']}/WordpressAdminSecrets")

    #     # EC2 Auto Scaling Group
    #     wordpress_asg = WordpressAutoScalingGroup(self, "WordpressASG", vpc=custom_vpc_instance.vpc,
    #                                               dns_name=cloudfront_distribution.distribution_domain_name,
    #                                               db_secret_name=rds_instance.secret_name,
    #                                               wp_secret_name=f"{config['projectName']}/WordpressAdminSecrets")


    #     # Secrets for WP Admin
    #     secretsmanager.Secret(self, 'WordpressAdminSecrets',
    #                           secret_name=f"{config['projectName']}/WordpressAdminSecrets",
    #                           description='Admin credentials to access Wordpress',
    #                           generate_secret_string={
    #                               'secret_string_template': json.dumps({
    #                                   'username': config['wordpress']['admin']['username'],
    #                                   'email': config['wordpress']['admin']['email'],
    #                               }),
    #                               'generate_string_key': 'password',
    #                           })
    #     #Secrets for WP Admin
    #     secretsmanager.Secret(self, 'WordpressAdminSecrets',
    #                         secret_name=wordpress_asg.wp_secret_name,  # Use the same wp_secret_name as in the AutoScalingGroup
    #                         description='Admin credentials to access Wordpress',
    #                         generate_secret_string={
    #                             'secret_string_template': json.dumps({
    #                                 'username': config['wordpress']['admin']['username'],
    #                                 'email': config['wordpress']['admin']['email'],
    #                             }),
    #                             'generate_string_key': 'password',
    #                         })


    #     # Fetch the user script from the file system as a string
    #     with open('lib/scripts/wordpress_install.sh', 'r') as file:
    #         user_script = file.read()

    #     # Replace the following variable substrings in the userScript
    #     # Replace the following variable substrings in the userScript
    #     replace_dict = {
    #         '_DB_SECRETS_PATH_': rds_instance.secret_name,
    #         '_WP_SECRETS_PATH_': f"{config['projectName']}/WordpressAdminSecrets",
    #         '_AWS_REGION_': config['stack']['region'],
    #         '_WP_DB_NAME_': config['wordpress']['site']['databaseName'],
    #         '_WP_SITE_TITLE_': config['wordpress']['site']['title'],
    #         '_WP_SITE_INSTALL_PATH_': config['wordpress']['site']['installPath'],
    #         '_WP_SITE_BASE_DOMAIN_': alb_instance.load_balancer_dns_name,
    #     }

    #     modified_user_script = self.replace_all_substrings(replace_dict, user_script)


    #     # Add a role that allows access to AWS Secrets Manager
    #     role = iam.Role(self, 'WordpressASGRole',
    #                     assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))

    #     role.add_to_policy(
    #         iam.PolicyStatement(
    #             effect=iam.Effect.ALLOW,
    #             actions=["secretsmanager:GetSecretValue"],
    #             resources=[rds_instance.secret_name, f"{config['projectName']}/WordpressAdminSecrets"],
    #         )
    #     )

    #     # Create and export out the autoscaling group
    #     self.asg = WordpressAutoScalingGroup(self, f"{config['projectName']}-asg",
    #                                          vpc=custom_vpc_instance.vpc,
    #                                          dns_name=alb_instance.load_balancer_dns_name,
    #                                          db_secret_name=rds_instance.secret_name,
    #                                          wp_secret_name=f"{config['projectName']}/WordpressAdminSecrets")

    #     cdk.CfnOutput(self, "ALBDnsName", value=alb_instance.load_balancer_dns_name)

    # @staticmethod
    # def replace_all_substrings(replace_dict, input_str):
    #     for key, value in replace_dict.items():
    #         input_str = input_str.replace(key, value)
    #     return input_str


# import aws_cdk as cdk
# from aws_cdk import Stack
# from constructs import Construct
# from lib.constructs.vpc import CustomVPC
# from lib.config import config
# from lib.constructs.rds import MySQLRdsInstance
# from lib.constructs.alb import WordpressApplicationLoadBalancer
# from lib.constructs.ec2 import WordpressAutoScalingGroup
# from aws_cdk import aws_secretsmanager as secretsmanager
# from aws_cdk import aws_iam as iam
# import json

# class WordpressEc2RdsStack(Stack):

#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # VPC -- fetch the custom VPC
#         custom_vpc_instance = CustomVPC(self, 'CustomVPC', {
#             'prefix': config['projectName'],
#             'cidr': '172.22.0.0/16',
#         })

#         # RDS -- create the MySQL database
#         rds_instance = MySQLRdsInstance(self, 'MySQLRDSInstance', {
#             'prefix': config['projectName'],
#             'vpc': custom_vpc_instance.vpc,
#             'user': 'wordpress_admin',
#             'database': 'awesome-wp-site-db',
#             'port': 3306,
#             'secretName': f"{config['projectName']}/rds/mysql/credentials",
#         })

#         # ALB -- for our single instance
#         alb_instance = WordpressApplicationLoadBalancer(self, 'WordpressALB', {
#             'prefix': config['projectName'],
#             'vpc': custom_vpc_instance.vpc,
#         })

#         # EC2 Auto Scaling Group
#         wordpress_asg = WordpressAutoScalingGroup(self, "WordpressASG", vpc=custom_vpc_instance.vpc,
#                                                   dns_name=alb_instance.load_balancer_dns_name,
#                                                   db_secret_name=rds_instance.secret_name,
#                                                   wp_secret_name=f"{config['projectName']}/WordpressAdminSecrets")

#         # Secrets for WP Admin
#         secretsmanager.Secret(self, 'WordpressAdminSecrets',
#                               secret_name=f"{config['projectName']}/WordpressAdminSecrets",
#                               description='Admin credentials to access Wordpress',
#                               generate_secret_string={
#                                   'secret_string_template': json.dumps({
#                                       'username': config['wordpress']['admin']['username'],
#                                       'email': config['wordpress']['admin']['email'],
#                                   }),
#                                   'generate_string_key': 'password',
#                               })

#         # Fetch the user script from the file system as a string
#         with open('lib/scripts/wordpress_install.sh', 'r') as file:
#             user_script = file.read()

#         # Replace the following variable substrings in the userScript
#         modified_user_script = self.replace_all_substrings(
#             [
#                 {'_DB_SECRETS_PATH_': rds_instance.secret_name},
#                 {'_WP_SECRETS_PATH_': f"{config['projectName']}/WordpressAdminSecrets"},
#                 {'_AWS_REGION_': config['env']['region']},
#                 {'_WP_DB_NAME_': config['wordpress']['site']['databaseName']},
#                 {'_WP_SITE_TITLE_': config['wordpress']['site']['title']},
#                 {'_WP_SITE_INSTALL_PATH_': config['wordpress']['site']['installPath']},
#                 {'_WP_SITE_BASE_DOMAIN_': alb_instance.load_balancer_dns_name},
#             ],
#             user_script
#         )

#         # Add a role that allows access to AWS Secrets Manager
#         role = iam.Role(self, 'WordpressASGRole',
#                         assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["secretsmanager:GetSecretValue"],
#                 resources=[rds_instance.secret_name, f"{config['projectName']}/WordpressAdminSecrets"],
#             )
#         )

#         # Create and export out the autoscaling group
#         self.asg = WordpressAutoScalingGroup(self, f"{config['projectName']}-asg",
#                                              vpc=custom_vpc_instance.vpc,
#                                              dns_name=alb_instance.load_balancer_dns_name,
#                                              db_secret_name=rds_instance.secret_name,
#                                              wp_secret_name=f"{config['projectName']}/WordpressAdminSecrets")

#         cdk.CfnOutput(self, "ALBDnsName", value=alb_instance.load_balancer_dns_name)

#     @staticmethod
#     def replace_all_substrings(replace_dict, input_str):
#         for key, value in replace_dict.items():
#             input_str = input_str.replace(key, value)
#         return input_str
# import aws_cdk as cdk
# from aws_cdk import Stack
# from constructs import Construct
# from lib.constructs.vpc import CustomVPC
# from lib.config import config
# from lib.constructs.rds import MySQLRdsInstance
# from lib.constructs.alb import WordpressApplicationLoadBalancer
# from lib.constructs.ec2 import WordpressAutoScalingGroup
# from aws_cdk import aws_secretsmanager as secretsmanager
# from aws_cdk import aws_iam as iam
# from aws_cdk import aws_cloudfront as cloudfront
# import json

# class WordpressEc2RdsStack(Stack):

#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # VPC -- fetch the custom VPC
#         custom_vpc_instance = CustomVPC(self, 'CustomVPC', {
#             'prefix': config['projectName'],
#             'cidr': '172.22.0.0/16',
#         })

#         # RDS -- create the MySQL database
#         rds_instance = MySQLRdsInstance(self, 'MySQLRDSInstance', {
#             'prefix': config['projectName'],
#             'vpc': custom_vpc_instance.vpc,
#             'user': 'wordpress_admin',
#             'database': 'awesome-wp-site-db',
#             'port': 3306,
#             'secretName': f"{config['projectName']}/rds/mysql/credentials",
#         })

#         # ALB -- for our single instance
#         alb_instance = WordpressApplicationLoadBalancer(self, 'WordpressALB', {
#             'prefix': config['projectName'],
#             'vpc': custom_vpc_instance.vpc,
#         })

#         # CloudFront distribution
#         cloudfront_distribution = cloudfront.CloudFrontWebDistribution(self, 'WordpressCloudFront',
#             origin_configs=[
#                 cloudfront.SourceConfiguration(
#                     custom_origin_source=cloudfront.CustomOriginConfig(
#                         domain_name=alb_instance.load_balancer_dns_name,
#                         origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
#                     ),
#                     behaviors=[cloudfront.Behavior(is_default_behavior=True)]
#                 ),
#             ],
#         )

#         # EC2 Auto Scaling Group
#         wordpress_asg = WordpressAutoScalingGroup(self, "WordpressASG", vpc=custom_vpc_instance.vpc,
#                                                   dns_name=cloudfront_distribution.distribution_domain_name,
#                                                   db_secret_name=rds_instance.secret_name,
#                                                   wp_secret_name=f"{config['projectName']}/WordpressAdminSecrets")

#         # Secrets for WP Admin
#         secretsmanager.Secret(self, 'WordpressAdminSecrets',
#                               secret_name=f"{config['projectName']}/WordpressAdminSecrets",
#                               description='Admin credentials to access Wordpress',
#                               generate_secret_string={
#                                   'secret_string_template': json.dumps({
#                                       'username': config['wordpress']['admin']['username'],
#                                       'email': config['wordpress']['admin']['email'],
#                                   }),
#                                   'generate_string_key': 'password',
#                               })

#         # Fetch the user script from the file system as a string
#         with open('lib/scripts/wordpress_install.sh', 'r') as file:
#             user_script = file.read()

#         # Replace the following variable substrings in the userScript
#         replace_dict = {
#             '_DB_SECRETS_PATH_': rds_instance.secret_name,
#             '_WP_SECRETS_PATH_': f"{config['projectName']}/WordpressAdminSecrets",
#             '_AWS_REGION_': config['stack']['region'],
#             '_WP_DB_NAME_': config['wordpress']['site']['databaseName'],
#             '_WP_SITE_TITLE_': config['wordpress']['site']['title'],
#             '_WP_SITE_INSTALL_PATH_': config['wordpress']['site']['installPath'],
#             '_WP_SITE_BASE_DOMAIN_': cloudfront_distribution.distribution_domain_name,
#         }

#         modified_user_script = self.replace_all_substrings(replace_dict, user_script)

#         # Add a role that allows access to AWS Secrets Manager
#         role = iam.Role(self, 'WordpressASGRole',
#                         assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))

#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["secretsmanager:GetSecretValue"],
#                 resources=[rds_instance.secret_name, f"{config['projectName']}/WordpressAdminSecrets"],
#             )
#         )

#         # Set deletion policy for CloudFront distribution
#         cloudfront_distribution.node.default_child.cfn_options.de

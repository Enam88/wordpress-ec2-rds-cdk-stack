from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_kms as kms
from aws_cdk import aws_iam as iam
from constructs import Construct
import aws_cdk as cdk

class MySecretsManager(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a secret
        secret = secretsmanager.Secret(
            self,
            "MySecret",
            secret_name="MySecretName",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "admin"}',
                generate_string_key='password',
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY  # Adjust removal policy as needed
        )

        # Create an alias for the secret
        secret.add_alias("alias/MySecretAlias")

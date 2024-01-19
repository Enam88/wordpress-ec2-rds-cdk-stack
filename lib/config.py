

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debugging: Print out the environment variables
print(f"Debug AWS_ACCOUNT_NUMBER: {os.getenv('AWS_ACCOUNT_NUMBER')}")
print(f"Debug AWS_REGION: {os.getenv('AWS_REGION')}")

# Define your config variables with default values
stage = os.environ.get('STAGE', 'dev')
aws_account_number = os.environ.get('AWS_ACCOUNT_NUMBER')
aws_region = os.environ.get('AWS_REGION')
deployed_by = os.environ.get('DEPLOYED_BY', os.environ.get('USER'))
project_name = f'wordpress-ec22-rds-{stage}'

# Additional WordPress configuration
wp_db_name = os.environ.get('WP_DB_NAME', 'wordpress_db')
wp_site_title = os.environ.get('WP_SITE_TITLE', 'My WordPress Site')
wp_site_install_path = os.environ.get('WP_SITE_INSTALL_PATH', '/var/www/html')
wp_site_base_domain = os.environ.get('WP_SITE_BASE_DOMAIN', 'example.com')

# Secrets paths
wp_db_secrets_path = "/rds/mysql/credentials"  # Database secrets path
wp_admin_secrets_arn = os.environ.get('WP_ADMIN_SECRETS_ARN')

# Create a config dictionary
config = {
    'stage': stage,
    'aws_account_number': aws_account_number,
    'aws_region': aws_region,
    'deployed_by': deployed_by,
    'project_name': project_name,
    'wordpress': {
        'site': {
            'databaseName': wp_db_name,
            'title': wp_site_title,
            'installPath': wp_site_install_path,
            'baseDomain': wp_site_base_domain,
        },
        'secrets': {
            'db_secrets_path': wp_db_secrets_path,  # Include DB secrets path
            'wp_admin_secrets_arn': wp_admin_secrets_arn,  # WP admin secrets ARN
        },
    },
    # ... (other configuration variables)
}

# Ensure all required environment variables are set
required_vars = ['AWS_ACCOUNT_NUMBER', 'AWS_REGION', 'WP_DB_NAME', 'WP_SITE_TITLE', 'WP_SITE_INSTALL_PATH', 'WP_SITE_BASE_DOMAIN', 'WP_ADMIN_SECRETS_ARN']
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

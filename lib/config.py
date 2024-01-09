# lib/config.py
import os

# Load environment variables from .env
# from dotenv import load_dotenv
# load_dotenv()

# This will be used in resource names
stage = os.environ.get('STAGE') or 'dev'

config = {
    # We'll use this prefix to help name our provisioned resources
    'projectName': f'wordpress-ec2-rds-{stage}',
    'stage': stage,
    'stack': {
        'account': os.environ.get('AWS_ACCOUNT_NUMBER'),
        'region': os.environ.get('AWS_REGION') or 'eu-west-3',
    },
    'wordpress': {
        'admin': {
            'username': os.environ.get('WP_ADMIN_USER') or 'admin',
            'email': os.environ.get('WP_ADMIN_EMAIL') or 'enam.akli@laplateforme.io',
        },
        'site': {
            'databaseName': os.environ.get('WP_DB_NAME') or 'awesome_wp_site_db',
            'title': os.environ.get('WP_SITE_TITLE') or 'awesome-wp-site',
            'installPath': os.environ.get('WP_SITE_INSTALL_PATH') or '/var/www/html/',
        },
        
    },
}

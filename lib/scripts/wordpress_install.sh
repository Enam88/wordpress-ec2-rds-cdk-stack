#!/bin/bash

sudo yum -y update
sudo yum -y install httpd php php-cli php-mysql jq mysql mysqladmin

# Fetch RDS Proxy Endpoint and Security Group ID from Parameter Store
# DB_HOST=$(aws ssm get-parameter --name '/myapp/rds/proxy-endpoint' --query 'Parameter.Value' --output text)
# DB_PROXY_SG_ID=$(aws ssm get-parameter --name '/myapp/rds/proxy-sg-id' --query 'Parameter.Value' --output text)

# Example commands to configure the application
# echo "DB_HOST=${DB_HOST}" >> /etc/myapp.conf
# More setup and configuration commands

# Retrieve DB credentials from AWS Secrets Manager
DB_CREDENTIALS=$(aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:eu-west-3:943240599753:secret:/rds/mysql/credentials-tg3CzL --query SecretString --output text --region eu-west-3)
DB_USER=$(echo $DB_CREDENTIALS | jq -r .username)
DB_PASS=$(echo $DB_CREDENTIALS | jq -r .password)
DB_HOST="wordpressec2rdsstackmysqlrordpressec22rdsdevrdsproxy76063ecf.proxy-ctolmm4tg8qx.eu-west-3.rds.amazonaws.com"
DB_PORT=$(echo $DB_CREDENTIALS | jq -r .port)
DB_NAME="wordpress"  # The database name should be defined here





sudo amazon-linux-extras install php7.4 -y
sudo service httpd start


# Install WordPress CLI
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp

WP_CREDENTIALS=$(aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:eu-west-3:943240599753:secret:WordpressAdminCredentials-bHpFRX --query SecretString --output text --region eu-west-3)
WP_ADMIN_USER=$(echo $WP_CREDENTIALS | jq -r .username)              # Replace with your admin username
WP_ADMIN_PASSWORD=$(echo $WP_CREDENTIALS | jq -r .password)      # Replace with your admin password
WP_ADMIN_EMAIL==$(echo $WP_CREDENTIALS | jq -r .email)   # Replace with your admin email

# Set up WordPress
WP_SITE_INSTALL_PATH="/var/www/html" # Replace with your actual installation path
WP_SITE_TITLE="Team-3 WordPress Site"    # Replace with your site title
WP_SITE_BASE_DOMAIN="example.com"  # Replace 'example.com' with your actual domain or IP address later

# DB_NAME="wordpress"  # The database name should be defined here


# Set the MYSQL_PWD environment variable for the current session
export MYSQL_PWD=$DB_PASS

mysql --user=DB_USER --password=DB_PASS --host=wordpressec2rdsstackmysqlrordpressec22rdsdevrdsproxy76063ecf.proxy-ctolmm4tg8qx.eu-west-3.rds.amazonaws.com ssl-mode=REQUIRED DB_NAME


# Create database and grant privileges using MySQL commands
mysql -h $DB_HOST -u $DB_USER -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
mysql -h $DB_HOST -u $DB_USER -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%'; FLUSH PRIVILEGES;"

# Unset the MYSQL_PWD environment variable after use
# unset MYSQL_PWD



# Download WP Core
sudo /usr/local/bin/wp core download --path=$WP_SITE_INSTALL_PATH

# Generate the wp-config.php file
sudo /usr/local/bin/wp core config --path=$WP_SITE_INSTALL_PATH --dbname=wordpress --dbuser=$DB_USER --dbpass=$DB_PASS --dbhost=$DB_HOST:$DB_PORT --extra-php <<PHP
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', true);
define('WP_MEMORY_LIMIT', '256M');
PHP

# Install WordPress
sudo /usr/local/bin/wp core install --path=$WP_SITE_INSTALL_PATH --url="http://localhost" --title="$WP_SITE_TITLE" --admin_user="$WP_ADMIN_USER" --admin_password="$WP_ADMIN_PASSWORD" --admin_email="$WP_ADMIN_EMAIL"

sudo service httpd restart


#!/usr/bin/env bash

# Author: @11808s8 - Adriano
# Email: adrianogsss@gmail.com
# Version: 1.1.0 - 07/04/2020
#
# @TODO: Refactor this, breaking parts into modules
# and include more comments/User feedbacks
#
# @TODO: Remove hardcoded credentials
# 
# !READ THIS! you should change the root credentials
#  and wordpress credentials accordingly.
#  This script needs to be refined in order to be
#  reproducible on a production environment.
#
# YOU CAN UPLOAD THIS ON YOUR USER DATA CONFIG FOR LAUNCHING AN INSTANCE
# NO NEED TO RUN IT INSIDE YOUR INSTANCE !!!
# (but you can run this inside your AWS EC2 instance if you want lol who am I to judge)
#

sudo yum update -y

# Install necessary packages

sudo yum install mariadb-server.x86_64 -y
sudo amazon-linux-extras install nginx1
sudo amazon-linux-extras install php7.2

# Start the processes
sudo systemctl enable mariadb 
sudo systemctl start mariadb 
sudo systemctl enable nginx 
sudo systemctl start nginx 
sudo systemctl enable php-fpm 
sudo systemctl start php-fpm 

# Configure the processes to start when the instance boots up
sudo chkconfig php-fpm on
sudo chkconfig nginx on
sudo chkconfig mariadb on

# Switch the APACHE lines on php-fpm (default ones) for nginx specific ones
sudo sed -i 's/user = apache/user = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/group = apache/group = nginx/' /etc/php-fpm.d/www.conf

# Create the www dir
sudo mkdir /var/www/

# Permission for us to download wordpress
sudo chown ec2-user:ec2-user /var/www/
cd /var/www/

# Download and extraction of wordpress
wget http://wordpress.org/latest.tar.gz
tar -xvf latest.tar.gz
rm latest.tar.gz
cd /var/

# Permission to nginx to use /var/www/
sudo chown -R nginx:nginx /var/www/

sudo systemctl stop mariadb
sudo mysql_install_db
sudo systemctl start mariadb


# Deprecated! 
#sudo mysql_secure_installation


# Adapted from here: https://bertvv.github.io/notes-to-self/2015/11/16/automating-mysql_secure_installation/

mysql --user=root <<EOF
USE mysql;
UPDATE user SET password=PASSWORD('root') WHERE User='root' AND Host = 'localhost';
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
FLUSH PRIVILEGES;
EOF

# ---

# CREATING THE DB
sudo mysqladmin -u 'root' -proot create 'wordpress'
# cd /tmp/

# ---- Deprecated ----
# CREATING THE WORDPRESS USER AND PASSWORD
# echo 'CREATE USER wordpress@localhost IDENTIFIED BY "wordpresspass";
# GRANT ALL PRIVILEGES ON wordpress.* to wordpress@localhost;' > mysql_wordpress_setup.sql
# sudo mysql -u root -proot wordpress < mysql_wordpress_setup.sql
# rm mysql_wordpress_setup.sql
# ---- ---------- ----

mysql --user=root -proot <<EOF
CREATE USER wordpress@localhost IDENTIFIED BY "wordpresspass";
GRANT ALL PRIVILEGES ON wordpress.* to wordpress@localhost;
EOF

# ---

# NGINX configuration for the server block! (vhost)

cd /tmp/
sudo echo "server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name wordpress;
    root /var/www/wordpress;
    index index.php;
    # Load configuration files for the default server block.
    include /etc/nginx/default.d/*.conf;
}" > wordpress.conf
sudo chown root:root wordpress.conf
sudo chmod 644 wordpress.conf
sudo mv wordpress.conf /etc/nginx/conf.d/


sudo echo "
# For more information on configuration, see:
#   * Official English Documentation: http://nginx.org/en/docs/
#   * Official Russian Documentation: http://nginx.org/ru/docs/
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;
# Load dynamic modules. See /usr/share/doc/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;
events {
    worker_connections 1024;
}
http {
    log_format  main  '$remote_addr - $remote_user [$time_local] \"$request\" '
                      '$status $body_bytes_sent \"$http_referer\" '
                      '\"$http_user_agent\" \"$http_x_forwarded_for\"';
    access_log  /var/log/nginx/access.log  main;
    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;
    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;
    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;
#    server {
#        listen       80 default_server;
#        listen       [::]:80 default_server;
#        server_name  _;
#        root         /usr/share/nginx/html;
#
#        # Load configuration files for the default server block.
#        include /etc/nginx/default.d/*.conf;
#
#        location / {
#        }
#
#        error_page 404 /404.html;
#            location = /40x.html {
#        }
#
#        error_page 500 502 503 504 /50x.html;
#            location = /50x.html {
#        }
#    }
# Settings for a TLS enabled server.
#
#    server {
#        listen       443 ssl http2 default_server;
#        listen       [::]:443 ssl http2 default_server;
#        server_name  _;
#        root         /usr/share/nginx/html;
#
#        ssl_certificate \"/etc/pki/nginx/server.crt\";
#        ssl_certificate_key \"/etc/pki/nginx/private/server.key\";
#        ssl_session_cache shared:SSL:1m;
#        ssl_session_timeout  10m;
#        ssl_ciphers PROFILE=SYSTEM;
#        ssl_prefer_server_ciphers on;
#
#        # Load configuration files for the default server block.
#        include /etc/nginx/default.d/*.conf;
#
#        location / {
#        }
#
#        error_page 404 /404.html;
#            location = /40x.html {
#        }
#
#        error_page 500 502 503 504 /50x.html;
#            location = /50x.html {
#        }
#    }
}
" > nginx.conf

sudo chown root:root nginx.conf
sudo chmod 644 nginx.conf
sudo mv nginx.conf /etc/nginx/

# The cherry on top
sudo service nginx restart
sudo service php-fpm restart
sudo service mariadb restart
# WordPress on AWS with Elastic Load Balancing and RDS USING PYTHON

This project sets up a highly available WordPress site on AWS using Elastic Load Balancer (ELB) and Amazon Relational Database Service (RDS) with RDS Proxy for database access.

## Architecture Overview

The architecture deploys WordPress on Amazon EC2 instances, which are scaled and managed by an Auto Scaling Group. An Elastic Load Balancer (ELB) distributes incoming traffic among the EC2 instances to ensure high availability and fault tolerance. The database layer is managed by Amazon RDS, with RDS Proxy to handle database connections efficiently, increasing the application's scalability and security.

### Components

- **Elastic Load Balancer (ELB)**: Distributes incoming application traffic across multiple EC2 instances, in multiple Availability Zones.
- **EC2 Instances**: Hosts the WordPress application, running on a scalable and secure environment.
- **RDS MySQL/PostgreSQL**: Provides a managed relational database environment for the persistent storage of WordPress data.
- **RDS Proxy**: Allows applications to pool and share database connections to improve scalability.

## Project Setup

1. **VPC Setup**:
   - Create a VPC with public and private subnets across multiple Availability Zones for high availability.

2. **EC2 Configuration**:
   - Launch EC2 instances within the public subnets of the VPC.
   - Configure an Auto Scaling Group to ensure that a specified number of EC2 instances are running.

3. **ELB Configuration**:
   - Set up an Elastic Load Balancer to route traffic to the EC2 instances.
   - Configure health checks to ensure traffic is routed only to healthy instances.

4. **RDS Configuration**:
   - Provision an RDS MySQL or PostgreSQL instance in the private subnets.
   - Enable Multi-AZ deployment for high availability.
   - Set up RDS Proxy to manage database connections.

5. **WordPress Installation**:
   - Install WordPress on EC2 instances and configure it to connect to the RDS database.
   - Use user data scripts to automate the WordPress setup process.

6. **Security Groups**:
   - Configure security groups for ELB to allow inbound traffic on port 80 (HTTP) and 443 (HTTPS).
   - Set up security groups for EC2 instances to allow traffic from ELB.
   - Restrict RDS access to the EC2 instances only.

## Deployment Steps

1. **Deploy Infrastructure**:
   - Use AWS CloudFormation or AWS CDK to define and deploy the infrastructure as code.

2. **Configure WordPress**:
   - Access the WordPress installation through the ELB's DNS name.
   - Complete the WordPress setup wizard using the database details configured in RDS.

3. **Verification**:
   - Verify that the WordPress site is accessible through the ELB's DNS name.
   - Ensure the site is functional and can withstand the failure of an EC2 instance or an Availability Zone.

## Monitoring and Maintenance

- **CloudWatch**: Set up monitoring and alarms for EC2 and RDS resources.
- **Backup**: Configure automated backups for RDS to ensure data durability.

## Additional Information

- **Documentation**: Refer to the [official AWS documentation](https://aws.amazon.com/documentation/) for detailed instructions on setting up each component.
- **Support**: For support and more information about best practices, visit the [AWS Support Center](https://aws.amazon.com/support/).

---

For further customization and scaling options, consider integrating additional AWS services such as Amazon CloudFront for content delivery and AWS WAF for web application firewall capabilities.




# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

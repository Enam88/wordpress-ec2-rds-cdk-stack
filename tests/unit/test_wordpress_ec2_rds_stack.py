import aws_cdk as core
import aws_cdk.assertions as assertions

from wordpress_ec2_rds.wordpress_ec2_rds_stack import WordpressEc2RdsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in wordpress_ec2_rds/wordpress_ec2_rds_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WordpressEc2RdsStack(app, "wordpress-ec2-rds")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

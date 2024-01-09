# create_env_file.py
with open('.env', 'w') as env_file:
    env_file.write("STAGE=dev\n")
    env_file.write("AWS_ACCOUNT_NUMBER=943240599753\n")
    env_file.write("AWS_REGION=eu-west-3\n")
    env_file.write("DEPLOYED_BY=enam.akli\n")



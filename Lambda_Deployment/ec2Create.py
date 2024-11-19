import json
import boto3

def lambda_handler(event, context):
    #Initialise AWS Resources
    ec2 = boto3.client('ec2')

    # Get VPC and Subnet IDs

    try:
        # Create EC2 Instances
        ec2_res = boto3.resource("ec2")
        web_server = ec2_res.create_instances(
            ImageId='',
            InstanceType="t2.micro",
            MaxCount=1, # Edit during PROD
            MinCount=1,
            SubnetId=public_sub_id,
            SecurityGroupIds = []   # Edit during PROD
        )

        app_server = ec2_res.create_instances(
            ImageId='',
            InstanceType="t2.micro",
            MaxCount=1, # Edit during PROD
            MinCount=1,
            SubnetId=private_sub_id,
            SecurityGroupIds = []    # Edit during PROD
        )

        # Response Json
        response = {
            "EC2 IDs (Web, App)": [web_server['InstanceId'], app_server['InstanceId']]
        }
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
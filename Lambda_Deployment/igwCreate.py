import json
import boto3


def lambda_handler(event, context):
    #Initialise AWS Resources
    ec2 = boto3.client('ec2')

    # Get VPC and Subnet IDs

    try:
        # Create and attach Internet Gateway
        igw = ec2.create_internet_gateway(TagSpecifications=[{
            'Key': "Name",
            'Value': "Internet Gateway"
        }])
        igw_id = igw["InternetGateway"]["InternetGatewayId"]
        ec2.attach_internet_gateway(VpcId=vpc_id, InternetGateway=igw_id)

        return {
            'statusCode': 200,
            'body': json.dumps("Internet Gateway Created.")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }


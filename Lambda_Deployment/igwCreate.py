import json
import boto3


def lambda_handler(event, context):
    #Initialise AWS Resources
    ec2 = boto3.client('ec2')
    
    # Get VPC ID
    vpc_id = ec2.describe_vpcs(Filters=[
        {
            'Name': "tag:Name",
            'Values': ["Project_VPC"]
        }
    ])['Vpcs'][0]['VpcId']

    try:
        # Create and attach Internet Gateway
        igw = ec2.create_internet_gateway(TagSpecifications=[{
            "ResourceType":"internet-gateway",
            "Tags": [
                {
                    'Key': "Name",
                    'Value': "Internet Gateway"
                }
            ]
        }])
        igw_id = igw["InternetGateway"]["InternetGatewayId"]
        ec2.attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=igw_id)

        return {
            'statusCode': 200,
            'body': json.dumps(f"Internet Gateway Created. {igw_id}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }


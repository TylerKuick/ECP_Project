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

    public_sub_id = ec2.describe_subnets(Filters=[{
        'Name': 'tag:Name',
        'Values': ["Public Subnet 1"]
    }])['Subnets'][0]['SubnetId']
    
    public_sub2_id = ec2.describe_subnets(Filters=[{
        'Name': 'tag:Name',
        'Values': ["Public Subnet 2"]
    }])['Subnets'][0]['SubnetId']

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


        # Create NAT Gateway 
        eip_addr = ec2.allocate_address(
            Domain="vpc",
            NetworkBorderGroup="us-east-1"
        )['AllocationId']

        eip_addr2 = ec2.allocate_address(
            Domain="vpc",
            NetworkBorderGroup="us-east-1"
        )['AllocationId']

        ec2.create_nat_gateway(
            AllocationId=eip_addr,
            SubnetId=public_sub_id,
            TagSpecifications=[{
                "ResourceType": "natgateway",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "ProjectNAT"
                    }
                ]
            }],
            ConnectivityType="public"
        )

        ec2.create_nat_gateway(
            AllocationId=eip_addr2,
            SubnetId=public_sub2_id,
            TagSpecifications=[{
                "ResourceType": "natgateway",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "ProjectNAT"
                    }
                ]
            }],
            ConnectivityType="public"
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f"Internet Gateway and NAT Gateway Created. {igw_id}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }


import json
import boto3

def lambda_handler(event, context):
    #Initialise AWS Resources
    ec2 = boto3.client('ec2')

    # Get VPC and Subnet IDs

    try: 
        # Create VPC
        vpc = ec2.create_vpc(CidrBlock = "10.0.0.0/16", TagSpecifications=[{
            'ResourceType':'vpc',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Project_VPC"
                }
            ]
        }])
        vpc_id = vpc['Vpc']['VpcId']
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={"Value": True})
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={"Value": True})

        # Create Security Group for HTTP / SSH Access
        try: 
            proj_sg = ec2.create_security_group(
                Description="WebSG",
                GroupName="Security Group for EC2 Instances",
                VpcId=vpc_id,
                TagSpecifications=[{
                    'ResourceType': 'security-group',
                    'Tags': [{
                        'Key': "Name",
                        "Value": "ProjectSG"
                    }]
                }]
            )
            
            proj_sg_id = proj_sg["GroupId"]

            inbound = ec2.authorize_security_group_ingress(
                GroupId=proj_sg_id,
                IpPermissions=[
                    {
                        'IpProtocal': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{"CidrIp": "0.0.0.0/0"}]},
                    {
                        'IpProtocal': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{"CidrIp": "0.0.0.0/0"}]
                    }
                ]
            )

            outbound = ec2.authorize_security_group_egress(
                GroupId=proj_sg_id,
                IpPermissions=[
                    {
                        'IpProtocal': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{"CidrIp": "0.0.0.0/0"}]},
                    {
                        'IpProtocal': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{"CidrIp": "0.0.0.0/0"}]
                    }
                ]
            ) 

            print(f"Security Group Succesfully defined and associated.{inbound}, {outbound}" )
        except Exception as e:
            print(e)


        # Config Subnets in us-east-1a
        public_sub = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.1.0/24",
            AvailabilityZone="us-east-1a", 
            TagSpecifications=[{
            'ResourceType':'subnet',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Public Subnet 1"
                }
            ]
        }])

        private_sub = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.2.0/24", 
            AvailabilityZone="us-east-1a", 
            TagSpecifications=[{
            'ResourceType':'subnet',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Private Subnet 1"
                }
            ]
        }]) 

        db_sub = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.3.0/24", 
            AvailabilityZone="us-east-1a", 
            TagSpecifications=[{
            'ResourceType':'subnet',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Private Subnet 2 (Database)"
                }
            ]
        }])


        # Config Subnets in us-east-1b
        public_sub2 = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.6.0/24", 
            AvailabilityZone="us-east-1b", 
            TagSpecifications=[{
            'ResourceType':'subnet',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Public Subnet 2"
                }
            ]
        }])

        private_sub2 = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.5.0/24", 
            AvailabilityZone="us-east-1b", 
            TagSpecifications=[{
            'ResourceType':'subnet',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Private Subnet 4"
                }
            ]
        }])

        db_sub2 = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.4.0/24", 
        AvailabilityZone="us-east-1b",
        TagSpecifications=[{
            'ResourceType':'subnet',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Private Subnet 3 (Database)"
                }
            ]
        }])

        # us-east-1a subnet IDs 
        public_sub_id = public_sub["Subnet"]["SubnetId"]
        private_sub_id = private_sub["Subnet"]["SubnetId"]
        db_sub_id = db_sub["Subnet"]["SubnetId"]

        # us-east-1b subnet IDs
        public_sub2_id = public_sub2["Subnet"]["SubnetId"]
        private_sub2_id = private_sub2["Subnet"]["SubnetId"]
        db_sub2_id = db_sub2["Subnet"]["SubnetId"]
        
        response = {
            "VPC ID": vpc_id,
            "Subnet IDs (us-east-1a)": [public_sub_id, private_sub_id, db_sub_id],
            "Subnet IDs (us-east-1b)": [public_sub2_id, private_sub2_id, db_sub2_id]
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
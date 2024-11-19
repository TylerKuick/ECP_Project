import json
import boto3

def lambda_handler(event, context):
    #Initialise AWS Resources
    ec2 = boto3.client('ec2')
    rds = boto3.client('rds')

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

        # Config Subnets
        public_sub = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.1.0/24", TagSpecifications=[{
            'ResourceType':'subnet',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Public Subnet 1"
                }
            ]
        }])
        private_sub = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.2.0/24", TagSpecifications=[{
            'ResourceType':'subnet',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Private Subnet 1"
                }
            ]
        }])
        db_sub = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.3.0/24", TagSpecifications=[{
            'ResourceType':'subnet',
            'Tags': [
                {
                    "Key": "Name",
                    "Value": "Private Subnet 2 (Database)"
                }
            ]
        }])
        public_sub_id = public_sub["Subnet"]["SubnetId"]
        private_sub_id = private_sub["Subnet"]["SubnetId"]
        db_sub_id = db_sub["Subnet"]["SubnetId"]

        # Create and attach Internet Gateway
        igw = ec2.create_internet_gateway(TagSpecifications=[{
            'Key': "Name",
            'Value': "Internet Gateway"
        }])
        igw_id = igw["InternetGateway"]["InternetGatewayId"]
        ec2.attach_internet_gateway(VpcId=vpc_id, InternetGateway=igw_id)

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

        # Create Primary RDS Instance
        primary_rds = rds.create_db_instances(
            DBName="PrimaryDB",
            DBInstanceIdentifier="primary-rds",
            AllocatedStorage=2,
            DBInstanceClass="db.t2.micro",
            Engine="mysql",
            MasterUsername="admin",
            MasterPassword="password",
            VPCSecurityGroupIds=[],  # Edit during PROD
            MultiAZ=True,
            PubliclyAccessible=False,
            SubnetIds=[private_sub_id]
        )
        # Create S3 Bucket

        # Setup CloudWatch Alarms

        return {
            'statusCode': 200,
            'body': json.dumps("Resources created successfully!")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
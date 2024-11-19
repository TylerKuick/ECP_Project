import json
import boto3

def lambda_handler(event, context):
    #Initialise AWS Resources
    ec2 = boto3.client('ec2')
    rds = boto3.client('rds')
    s3 = boto3.client('s3')

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
            AllocatedStorage=20,
            DBInstanceClass="db.t3.micro",
            Engine="mysql",
            MasterUsername="admin",
            MasterPassword="password",
            VPCSecurityGroupIds=[],  # Edit during PROD
            MultiAZ=False,
            PubliclyAccessible=False,
            SubnetIds=[db_sub_id]
        )

        # Add RDS Security Group to RDS Instance
        try:
            rds.create_db_security_group(
                DBSecurityGroupName="RDSSG",
                DBSecurityGroupDescription="Security Group to connect RDS with EC2 Instances",
                Tags=[{
                    "Key": "Name",
                    "Values": "RDSSG"
                }]
            )

            rds.modify_db_instance(
                DBInstanceIdentifier="primary-rds",
                DBSecurityGroups=["RDSSG"]
            )

            print("Successfully created and associated RDS Security Group")
        except Exception as e:
            print(e)


        # Create S3 Bucket
        bucket_name="Project Web Bucket"
        s3.create_bucket(Bucket=bucket_name, CreateBucketConstraint={'LocationConstraint': 'us-east-1'})

        # Bucket Policy 
        bucket_policy = {
            "Version": "2024-11-19",
            "Statement": {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        }
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))


        # Setup CloudWatch Alarms
        


        # Response Json
        response = {
            "VPC ID": vpc_id,
            "Subnet IDs (Public, Private, DB)": [public_sub_id, private_sub_id, db_sub_id],
            "EC2 IDs (Web, App)": [web_server['InstanceId'], app_server['InstanceId']],
            "RDS ID": primary_rds["DBInstance"],
            "S3 Bucket Name": bucket_name 
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
import json
import boto3

def lambda_handler(event, context):
    #Initialise AWS Resources
    ec2 = boto3.client('ec2')
    elbv2 = boto3.client('elbv2')
    autoscaler = boto3.client('autoscaling')

    # Get VPC ID and Subnet IDs
    vpc_id = ec2.describe_vpcs(Filters=[
        {
            'Name': "tag:Name",
            'Values': ["Project_VPC"]
        }
    ])['Vpcs'][0]['VpcId']
    proj_sg = ec2.describe_security_groups(Filters=[{
        'Name':'tag:Name',
        'Values':["ProjectSG"]
    }])['SecurityGroups'][0]['GroupId']

    public_sub_id = ec2.describe_subnets(Filters=[{
        'Name': 'tag:Name',
        'Values': ["Public Subnet 1"]
    }])['Subnets'][0]['SubnetId']

    public_sub2_id = ec2.describe_subnets(Filters=[{
        'Name': 'tag:Name',
        'Values': ["Public Subnet 2"]
    }])['Subnets'][0]['SubnetId']
    
    private_sub_id = ec2.describe_subnets(Filters=[{
        'Name': 'tag:Name',
        'Values': ["Private Subnet 1"]
    }])['Subnets'][0]['SubnetId']

    private_sub4_id = ec2.describe_subnets(Filters=[{
        'Name': 'tag:Name',
        'Values': ["Private Subnet 4"]
    }])['Subnets'][0]['SubnetId']


    try:
        # Create EC2 Instances
        ec2_res = boto3.resource("ec2")
        web_server = ec2_res.create_instances(
            ImageId='ami-012967cc5a8c9f891',
            InstanceType="t2.micro",
            MaxCount=1, # Edit during PROD
            MinCount=1,
            SubnetId=public_sub_id,
            SecurityGroupIds = [proj_sg],   # Edit during PROD
            TagSpecifications= [{
                'ResourceType': "instance",
                "Tags": [
                    {
                        'Key': 'Name',
                        'Value': "Web Server"
                    }
                ]
            }]
        )

        app_server = ec2_res.create_instances(
            ImageId='ami-012967cc5a8c9f891',
            InstanceType="t2.micro",
            MaxCount=1, # Edit during PROD
            MinCount=1,
            SubnetId=private_sub_id,
            SecurityGroupIds = [proj_sg],    # Edit during PROD
            TagSpecifications= [{
                'ResourceType': "instance",
                "Tags": [
                    {
                        'Key': 'Name',
                        'Value': "App Server"
                    }
                ]
            }]
        )

        # Describe EC2 Instances (Get ID of Web and App Server)
        desc_ec2 = ec2.describe_instances(Filters=[{
            "Name": "tag:Name",
            "Values": ["Web Server", "App Server"]
        }])
        
        web_ids = []        
        web_servers = desc_ec2['Reservations'][1]['Instances']
        for web_server in web_servers: 
            web_ids.append(web_server["InstanceId"])
        
        app_ids = [] 
        app_servers = desc_ec2['Reservations'][0]['Instances'][0]['InstanceId']
        for app_server in app_servers: 
            app_ids.append(app_server["InstanceId"])
        

        # Response Json
        response = {
            "EC2 IDs (Web, App)": f"{web_ids}, {app_ids} "
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
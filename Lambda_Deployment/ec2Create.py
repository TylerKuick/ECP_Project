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
    
        web_id = desc_ec2['Reservations'][1]['Instances'][0]['InstanceId']
        app_id = desc_ec2['Reservations'][0]['Instances'][0]['InstanceId']


        # Create Load Balancers (1 to Web Servers, 1 to App Servers)     
        # Define Target Groups and Targets for Web Servers
        webHTTPTG_ARN = elbv2.create_target_group(
            Name="web-server-http-tg",
            Protocol="HTTP",
            Port="80",
            VpcId=vpc_id,
            TargetType="instance"
        )["TargetGroups"][0]["TargetGroupArn"]
        webHTTPSTG_ARN = elbv2.create_target_group(
            Name="web-server-https-tg",
            Protocol="HTTPS",
            Port="443",
            VpcId=vpc_id,
            TargetType="instance"
        )["TargetGroups"][0]["TargetGroupArn"]

        # Register HTTP / HTTPS Targets for Web Servers
        elbv2.register_targets(
            TargetGroupArn=webHTTPTG_ARN,
            Targets=[{
                'Id': web_id,
                'Port': 80
            }]
        )
        elbv2.register_targets(
            TargetGroupArn=webHTTPSTG_ARN,
            Targets=[{
                'Id': web_id,
                'Port': 443
            }]
        )

        # Create Load Balancer for Web Servers
        web_server_LB_ARN = elbv2.create_load_balancer(
            Name="Web Server Load Balancer",
            Subnets=[public_sub_id, public_sub2_id],
            SecurityGroups="",
            Type="application",
            Scheme="internet-facing",
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'WebLB'
                }
            ]
        )['LoadBalancers'][0]['LoadBalancerArn']

        # Create Listener for Web Servers 
        elbv2.create_listener(
            LoadBalancerArn=web_server_LB_ARN,
            Protocol="HTTP",
            Port=80,
            DefaultActions=[{
                'Type': 'forward',
                'TargetGroupArn': webHTTPTG_ARN
            }]
        )
        elbv2.create_listener(
            LoadBalancerArn=web_server_LB_ARN,
            Protocol="HTTPS",
            Port=443,
            DefaultActions=[{
                'Type': 'forward',
                'TargetGroupArn': webHTTPTG_ARN
            }]
        )

        # Define Target Groups and Targets for Web Servers
        appHTTPTG_ARN = elbv2.create_target_group(
            Name="app-server-tg",
            Protocol="HTTP",
            Port="80",
            VpcId=vpc_id,
            TargetType="instance"
        )["TargetGroups"][0]["TargetGroupArn"]

        appHTTPSTG_ARN = elbv2.create_target_group(
            Name="app-server-tg",
            Protocol="HTTPS",
            Port="443",
            VpcId=vpc_id,
            TargetType="instance"
        )["TargetGroups"][0]["TargetGroupArn"]

        # Register HTTP / HTTPS Targets for App Servers
        elbv2.register_targets(
            TargetGroupArn=appHTTPTG_ARN,
            Targets=[{
                'Id': web_id,
                'Port': 80
            }]
        )
        elbv2.register_targets(
            TargetGroupArn=appHTTPSTG_ARN,
            Targets=[{
                'Id': web_id,
                'Port': 443
            }]
        )

        # Create Load Balancer for App Servers
        app_server_LB_ARN = elbv2.create_load_balancer(
            Name="App Server Load Balancer",
            Subnets=[private_sub_id, private_sub4_id],
            SecurityGroups="",
            Type="application",
            Scheme="internal",
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'AppLB'
                }
            ]
        )['LoadBalancers'][0]['LoadBalancerArn']

        # Create Listener for Web Servers 
        elbv2.create_listener(
            LoadBalancerArn=app_server_LB_ARN,
            Protocol="HTTP",
            Port=80,
            DefaultActions=[{
                'Type': 'forward',
                'TargetGroupArn': appHTTPTG_ARN
            }]
        )
        elbv2.create_listener(
            LoadBalancerArn=app_server_LB_ARN,
            Protocol="HTTPS",
            Port=443,
            DefaultActions=[{
                'Type': 'forward',
                'TargetGroupArn': appHTTPTG_ARN
            }]
        )
        
        # Create Auto Scaling Groups (1 to Web Servers, 1 to App Servers)

        # Create Launch Template for Web Servers
        web_server_LT = ec2.create_launch_template(
            LaunchTemplateName="webserver-launchtemp",
            LaunchTemplateData={
                'IamInstanceProfile': {
                    'Arn': "",  # Edit in PROD
                    'Name': "LabRole"
                },
                'ImageId': "ami-012967cc5a8c9f891",
                'InstanceType':"t2.micro",
                'TagSpecifications': [{
                    'ResourceType': "instance",
                    'Tags': [{
                        "Key": "Name",
                        "Value": "Web Server"
                    }]
                }]
            })

        autoscaler.create_auto_scaling_group(
            AutoScalingGroupName="WebASG",
            LaunchTemplate={"LaunchTemplateName": "webserver-launchtemp"},
            MinSize=1,
            MaxSize=1,
            DesiredCapacity=1,
            VPCZoneIdentifier=f"{public_sub_id}, {public_sub2_id}",
            LoadBalancerNames=["Web Server Load Balancer"],
            TargetGroupARNs=[webHTTPTG_ARN, webHTTPSTG_ARN]
        )


        # Create Launch Template for Web Servers
        app_server_LT = ec2.create_launch_template(
            LaunchTemplateName="appserver-launchtemp",
            LaunchTemplateData={
                'IamInstanceProfile': {
                    'Arn': "",  # Edit in PROD
                    'Name': "LabRole"
                },
                'ImageId': "ami-012967cc5a8c9f891",
                'InstanceType':"t2.micro",
                'TagSpecifications': [{
                    'ResourceType': "instance",
                    'Tags': [{
                        "Key": "Name",
                        "Value": "App Server"
                    }]
                }]
            })
        
        autoscaler.create_auto_scaling_group(
            AutoScalingGroupName="AppASG",
            LaunchTemplate={"LaunchTemplateName": "appserver-launchtemp"},
            MinSize=1,
            MaxSize=1,
            DesiredCapacity=1,
            VPCZoneIdentifier=f"{private_sub_id}, {private_sub4_id}",
            LoadBalancerNames=["Web Server Load Balancer"],
            TargetGroupARNs=[webHTTPTG_ARN, webHTTPSTG_ARN]
        )


        # Response Json
        response = {
            "EC2 IDs (Web, App)": f"{web_id}, {app_id} "
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
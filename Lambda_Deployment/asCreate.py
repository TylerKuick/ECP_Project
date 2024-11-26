import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    ec2 = boto3.client('ec2')
    elbv2 = boto3.client('elbv2')
    autoscaler = boto3.client('autoscaling')

    # Subnet IDs 
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

    # ELB Waiter
    waiter = elbv2.get_waiter("load_balancer_available")
   
    try:
         # Get Load Balancer and TG Info
        webHTTPTG_ARN = elbv2.describe_target_groups(
            Names=["web-server-http-tg"]
        )['TargetGroups'][0]['TargetGroupArn']

        appHTTPTG_ARN = elbv2.describe_target_groups(
            Names=["app-server-http-tg"]
        )

        # Wait for ELB to be available
        waiter.wait(
            Names=["app-server-LB","web-server-LB"]
        )
        # Create Auto Scaling Groups (1 to Web Servers, 1 to App Servers)

        # Create Launch Template for Web Servers
        web_server_LT = ec2.create_launch_template(
            LaunchTemplateName="webserver-launchtemp",
            LaunchTemplateData={
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
            TargetGroupARNs=[webHTTPTG_ARN] #, webHTTPSTG_ARN
        )


        # Create Launch Template for app Servers
        app_server_LT = ec2.create_launch_template(
            LaunchTemplateName="appserver-launchtemp",
            LaunchTemplateData={
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
            TargetGroupARNs=[appHTTPTG_ARN] #, webHTTPSTG_ARN
        )

        return {
            'statusCode': 200,
            'body': json.dumps('Successfully setup Auto Scaling Group!')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    ec2 = boto3.client('ec2')
    elbv2 = boto3.client('elbv2')
    
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

    # Create Load Balancers (1 to Web Servers, 1 to App Servers)     
    # Define Target Groups and Targets for Web Servers
    try: 
        # Describe EC2 Instances (Get ID of Web and App Server)
        desc_ec2 = ec2.describe_instances(Filters=[{
            "Name": "tag:Name",
            "Values": ["Web Server", "App Server"]
        },
        {
            "Name":"instance-state-name",
            "Values": ["running"]
        }])
        
        web_ids = []        
        web_servers = desc_ec2['Reservations'][1]['Instances']
        for web_server in web_servers: 
            web_ids.append(web_server["InstanceId"])
        
        app_ids = [] 
        app_servers = desc_ec2['Reservations'][0]['Instances']
        for app_server in app_servers: 
            app_ids.append(app_server["InstanceId"])
        

        webHTTPTG_ARN = elbv2.create_target_group(
            Name="web-server-http-tg",
            Protocol="HTTP",
            Port=80,
            VpcId=vpc_id,
            TargetType="instance"
        )["TargetGroups"][0]["TargetGroupArn"]
        # webHTTPSTG_ARN = elbv2.create_target_group(
        #     Name="web-server-https-tg",
        #     Protocol="HTTPS",
        #     Port=443,
        #     VpcId=vpc_id,
        #     TargetType="instance"
        # )["TargetGroups"][0]["TargetGroupArn"]

        # Register HTTP / HTTPS Targets for Web Servers
        elbv2.register_targets(
            TargetGroupArn=webHTTPTG_ARN,
            Targets=[{
                'Id': web_ids[0],
                'Port': 80
            }]
        )
        # elbv2.register_targets(
        #     TargetGroupArn=webHTTPSTG_ARN,
        #     Targets=[{
        #         'Id': web_ids[0],
        #         'Port': 443
        #     }]
        # )

        # Create Load Balancer for Web Servers
        web_server_LB_ARN = elbv2.create_load_balancer(
            Name="web-server-LB",
            Subnets=[public_sub_id, public_sub2_id],
            SecurityGroups=[proj_sg],
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
        # elbv2.create_listener(
        #     LoadBalancerArn=web_server_LB_ARN,
        #     Protocol="HTTPS",
        #     Port=443,
        #     DefaultActions=[{
        #         'Type': 'forward',
        #         'TargetGroupArn': webHTTPTG_ARN
        #     }]
        # )

        # Define Target Groups and Targets for Web Servers
        appHTTPTG_ARN = elbv2.create_target_group(
            Name="app-server-http-tg",
            Protocol="HTTP",
            Port=80,
            VpcId=vpc_id,
            TargetType="instance"
        )["TargetGroups"][0]["TargetGroupArn"]

        # appHTTPSTG_ARN = elbv2.create_target_group(
        #     Name="app-server-https-tg",
        #     Protocol="HTTPS",
        #     Port=443,
        #     VpcId=vpc_id,
        #     TargetType="instance"
        # )["TargetGroups"][0]["TargetGroupArn"]

        # Register HTTP / HTTPS Targets for App Servers
        elbv2.register_targets(
            TargetGroupArn=appHTTPTG_ARN,
            Targets=[{
                'Id': app_ids[0],
                'Port': 80
            }]
        )
        # elbv2.register_targets(
        #     TargetGroupArn=appHTTPSTG_ARN,
        #     Targets=[{
        #         'Id': app_ids[0],
        #         'Port': 443
        #     }]
        # )

        # Create Load Balancer for App Servers
        app_server_LB_ARN = elbv2.create_load_balancer(
            Name="app-server-LB",
            Subnets=[private_sub_id, private_sub4_id],
            SecurityGroups=[proj_sg],
            Type="application",
            Scheme="internal",
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'AppLB'
                }
            ]
        )['LoadBalancers'][0]['LoadBalancerArn']

        # Create Listener for App Servers 
        elbv2.create_listener(
            LoadBalancerArn=app_server_LB_ARN,
            Protocol="HTTP",
            Port=80,
            DefaultActions=[{
                'Type': 'forward',
                'TargetGroupArn': appHTTPTG_ARN
            }]
        )
        # elbv2.create_listener(
        #     LoadBalancerArn=app_server_LB_ARN,
        #     Protocol="HTTPS",
        #     Port=443,
        #     DefaultActions=[{
        #         'Type': 'forward',
        #         'TargetGroupArn': appHTTPTG_ARN
        #     }]
        # )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully setup ELBs!')
        }
    except Exception as e: 
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)},  {app_ids}, {web_ids}")
        }
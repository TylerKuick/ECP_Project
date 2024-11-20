import json
import boto3

def lambda_handler(event, context):
    #Initialise AWS Resources
    rds = boto3.client('rds')
    ec2 = boto3.client('ec2')
    # Get VPC and Subnet IDs
    db_sub_id = ec2.describe_subnets(Filters=[{
        'Name': 'tag:Name',
        'Values': ["Private Subnet 2 (Database)"]
    }])['Subnets'][0]['SubnetId']

    proj_sg = ec2.describe_security_groups(Filters=[{
        'Name':'tag:Name',
        'Values':["ProjectSG"]
    }])['SecurityGroups'][0]['GroupId']


    try:
        # Create DB Subnet Group 
        rds.create_db_subnet_group(
            DBSubnetGroupName = 'ProjectRDS',
            DBSubnetGroupDescription='RDS Subnet Group',
            SubnetIds=[db_sub_id]
        )

        # Create Primary RDS Instance
        primary_rds = rds.create_db_instance(
            DBName="PrimaryDB",
            DBInstanceIdentifier="primary-rds",
            AllocatedStorage=20,
            DBInstanceClass="db.t3.micro",
            Engine="mysql",
            MasterUsername="admin",
            MasterUserPassword="password",
            VpcSecurityGroupIds=[proj_sg],  
            MultiAZ=False,
            PubliclyAccessible=False,
            DBSubnetGroupName=["ProjectRDS"]
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

        response = {
            "RDS ID": primary_rds["DBInstance"]
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


import json
import boto3

def lambda_handler(event, context):
    #Initialise AWS Resources
    rds = boto3.client('rds')

    # Get VPC and Subnet IDs

    try:
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


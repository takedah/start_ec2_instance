import time

import boto3
import botocore
from botocore.config import Config

# エラー時のリトライ数を設定
config = Config(retries={"total_max_attempts": 10, "mode": "standard"})
# EC2 のリージョンを指定
region = "ap-northeast-1"
# 対象のインスタンス ID をリストに列挙する
instances = [
    "対象のインスタンス ID",
]


def lambda_handler(event, context):
    ec2 = boto3.client("ec2", config=config, region_name=region)
    action = event["Action"]
    instance_states = dict()
    try:
        if action == "Start":
            ec2.start_instances(InstanceIds=instances)
        elif action == "Stop":
            ec2.stop_instances(InstanceIds=instances)
        else:
            return {
                "statusCode": 200,
                "body": "Action パラメーターが不正です。",
            }

        time.sleep(15)
        statuses = ec2.describe_instance_status(InstanceIds=instances, IncludeAllInstances=True)
        for status in statuses["InstanceStatuses"]:
            instance_states[status["InstanceId"]] = status["InstanceState"]["Name"]

        return {
            "statusCode": 200,
            "body": {
                "Action": action,
                "States": instance_states,
            },
        }
    except botocore.exceptions.ClientError as error:
        return {
            "statusCode": 503,
            "body": error.response["Error"]["Message"],
        }

import json
import os

# use by serverless lambda
def lambda_handler(event, context):
    print("Full event data:")
    print(event)

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}

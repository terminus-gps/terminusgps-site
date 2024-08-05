import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str) -> str:
    # Create a Secrets Manager client
    session = boto3.session.Session(profile_name="secret-rotator")
    client = session.client(
        service_name="secretsmanager",
        region_name="us-east-1",
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    return get_secret_value_response['SecretString']

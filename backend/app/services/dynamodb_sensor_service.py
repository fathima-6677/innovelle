import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from boto3.dynamodb.conditions import Key
import os
import logging

logger = logging.getLogger(__name__)

class DynamoDBSensorService:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "ap-south-1")
        try:
            self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
            self.table = self.dynamodb.Table("AutiGuardSensorData")
            logger.info(f"DynamoDB connection success. Table: AutiGuardSensorData initialized in {self.region}.")
        except NoCredentialsError:
            logger.error("No AWS credentials found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing DynamoDB: {e}")
            raise

    def get_latest_sensor_data(self, device_id: str):
        logger.info(f"DynamoDB query: latest sensor data for {device_id}")
        try:
            response = self.table.query(
                KeyConditionExpression=Key('device_id').eq(device_id),
                ScanIndexForward=False, # Newest item first
                Limit=1
            )
            items = response.get('Items', [])
            logger.info(f"Returned items: {len(items)}")
            return items[0] if items else None
        except ClientError as e:
            logger.error(f"ClientError querying latest sensor data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error querying latest sensor data: {e}")
            raise

    def get_sensor_history(self, device_id: str, limit: int = 100):
        logger.info(f"DynamoDB query: sensor history for {device_id}, limit {limit}")
        try:
            response = self.table.query(
                KeyConditionExpression=Key('device_id').eq(device_id),
                ScanIndexForward=False, # Newest items first
                Limit=limit
            )
            items = response.get('Items', [])
            logger.info(f"Returned items: {len(items)}")
            return items
        except ClientError as e:
            logger.error(f"ClientError querying sensor history: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error querying sensor history: {e}")
            raise

    def update_stress_score(self, device_id: str, timestamp: int, score: int):
        try:
            self.table.update_item(
                Key={'device_id': device_id, 'timestamp': timestamp},
                UpdateExpression="set stress_score = :s",
                ExpressionAttributeValues={':s': score}
            )
            logger.info(f"Updated stress_score to {score} for device {device_id} at {timestamp}")
        except Exception as e:
            logger.error(f"Failed to update stress_score: {e}")

sensor_db_service = DynamoDBSensorService()

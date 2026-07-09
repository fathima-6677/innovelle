import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from decimal import Decimal

# Helper functions to convert floats to Decimals and vice versa
def float_to_decimal(obj):
    if isinstance(obj, float):
        # Convert to string first to avoid precision issues in Decimal
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(x) for x in obj]
    return obj

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        # Convert to int if it's a whole number, else float
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(x) for x in obj]
    return obj

class DynamoDBWrapper:
    def __init__(self):
        self.use_mock = settings.MOCK_AWS and not settings.DYNAMODB_ENDPOINT
        self.mock_store = {} # PK -> {SK -> Item}

        if not self.use_mock:
            params = {}
            if settings.DYNAMODB_ENDPOINT:
                params["endpoint_url"] = settings.DYNAMODB_ENDPOINT
            if settings.AWS_ACCESS_KEY_ID:
                params["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            if settings.AWS_SECRET_ACCESS_KEY:
                params["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            params["region_name"] = settings.AWS_DEFAULT_REGION

            self.resource = boto3.resource("dynamodb", **params)
            self.client = boto3.client("dynamodb", **params)
            self.table = self.resource.Table(settings.DYNAMODB_TABLE)

    def get_item(self, pk: str, sk: str):
        if self.use_mock:
            item = self.mock_store.get(pk, {}).get(sk)
            return decimal_to_float(item) if item else None

        try:
            response = self.table.get_item(Key={"PK": pk, "SK": sk})
            item = response.get("Item")
            return decimal_to_float(item) if item else None
        except ClientError as e:
            print(f"DynamoDB get_item error: {e}")
            return None

    def put_item(self, item: dict):
        # Deep convert floats to Decimals for DynamoDB compatibility
        item_decimal = float_to_decimal(item)

        if self.use_mock:
            pk = item_decimal.get("PK")
            sk = item_decimal.get("SK")
            if pk not in self.mock_store:
                self.mock_store[pk] = {}
            self.mock_store[pk][sk] = item_decimal
            return True

        try:
            self.table.put_item(Item=item_decimal)
            return True
        except ClientError as e:
            print(f"DynamoDB put_item error: {e}")
            return False

    def delete_item(self, pk: str, sk: str):
        if self.use_mock:
            if pk in self.mock_store and sk in self.mock_store[pk]:
                del self.mock_store[pk][sk]
                if not self.mock_store[pk]:
                    del self.mock_store[pk]
                return True
            return False

        try:
            self.table.delete_item(Key={"PK": pk, "SK": sk})
            return True
        except ClientError as e:
            print(f"DynamoDB delete_item error: {e}")
            return False

    def query_by_pk(self, pk: str, sk_prefix: str | None = None):
        if self.use_mock:
            items = []
            pk_items = self.mock_store.get(pk, {})
            for sk, item in pk_items.items():
                if sk_prefix is None or sk.startswith(sk_prefix):
                    items.append(decimal_to_float(item))
            return items

        try:
            if sk_prefix:
                key_condition = boto3.dynamodb.conditions.Key("PK").eq(pk) & boto3.dynamodb.conditions.Key("SK").begins_with(sk_prefix)
            else:
                key_condition = boto3.dynamodb.conditions.Key("PK").eq(pk)
            response = self.table.query(KeyConditionExpression=key_condition)
            return decimal_to_float(response.get("Items", []))
        except ClientError as e:
            print(f"DynamoDB query error: {e}")
            return []

    def query_gsi1(self, gsi1_pk: str, gsi1_sk_prefix: str | None = None):
        if self.use_mock:
            # Search all items in mock_store for GSI1 matches
            items = []
            for pk, sk_dict in self.mock_store.items():
                for sk, item in sk_dict.items():
                    if item.get("GSI1PK") == gsi1_pk:
                        gsi1_sk = item.get("GSI1SK", "")
                        if gsi1_sk_prefix is None or gsi1_sk.startswith(gsi1_sk_prefix):
                            items.append(decimal_to_float(item))
            return items

        try:
            if gsi1_sk_prefix:
                key_condition = boto3.dynamodb.conditions.Key("GSI1PK").eq(gsi1_pk) & boto3.dynamodb.conditions.Key("GSI1SK").begins_with(gsi1_sk_prefix)
            else:
                key_condition = boto3.dynamodb.conditions.Key("GSI1PK").eq(gsi1_pk)
            response = self.table.query(
                IndexName="GSI1",
                KeyConditionExpression=key_condition
            )
            return decimal_to_float(response.get("Items", []))
        except ClientError as e:
            print(f"DynamoDB GSI1 query error: {e}")
            return []

db = DynamoDBWrapper()

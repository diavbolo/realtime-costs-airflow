import logging
import boto3

logger = logging.getLogger(__name__)

class DynamoDB:

    def __init__(self):
        try:    
            self.client = boto3.client('dynamodb')
            self.response = None
        except Exception as e:
            logger.exception(e)
            raise

    def get_item(self, table, key):
        try:
            self.response = self.client.get_item(
                TableName = table,
                Key = key
            )
        except Exception as e:
            logger.exception(e)
            raise
    
        return self.response

    def get_scan(self, table, ExpressionAttributeNames, ExpressionAttributeValues, FilterExpression):
        try:
            self.response = self.client.get_paginator('scan').paginate(
                TableName = table, 
                ExpressionAttributeNames = ExpressionAttributeNames, 
                ExpressionAttributeValues = ExpressionAttributeValues, 
                FilterExpression = FilterExpression
            )
        except Exception as e:
            logger.exception(e)
            raise
    
        return self.response

    def get_config(self, item=None):
        self.response = self.get_item(table = 'config', key = {'id': {'S': item}})
        return self.response['Item']['value']['S']

    def get_accounts(self, table='status', subscribed=None):
        self.response = self.get_scan(
            table, 
            ExpressionAttributeNames = {"#status": "status"}, 
            ExpressionAttributeValues = {":on": {'S': subscribed}}, 
            FilterExpression = '#status = :on'
        )
        return self.response

    def get_subscribed_accounts(self):
        return self.get_accounts(table='status', subscribed='on')

    def get_unsubscribed_accounts(self):
        return self.get_accounts(table='status', subscribed='off')
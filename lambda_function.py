import boto3
import json
from custom_encoder import CustomEncoder
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = "meditrack-user-info"
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
emailPath = '/email'
passwordPath = '/password'
usernamePath = '/username'

def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    body = event.get('body', '')

    logger.info(f'Raw request body: {body}')  # Log the raw request body

    try:
        if httpMethod == getMethod and path == emailPath:
            response = getEmail(event['queryStringParameters']['email'])
        elif httpMethod == postMethod and path == emailPath:
            response = saveEmail(json.loads(body))
        elif httpMethod == patchMethod and path == emailPath:
            requestBody = json.loads(body)
            response = modifyEmail(requestBody['email'], requestBody['updateKey'], requestBody['updateValue'])
        elif httpMethod == deleteMethod and path == emailPath:
            requestBody = json.loads(body)
            response = deleteEmail(requestBody['email'])
        else:
            response = buildResponse(404, 'Not Found')
    except json.JSONDecodeError as e:
        logger.exception('JSON decode error')
        response = buildResponse(400, {'Message': 'Bad Request', 'Error': 'Invalid JSON'})
    except Exception as e:
        logger.exception('Error processing request')
        response = buildResponse(500, {'Message': 'Internal Server Error', 'Error': str(e)})

    return response

def getEmail(email):
    try:
        response = table.get_item(Key={'email': email})
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'Email not found'})
    except Exception as e:
        logger.exception('Unable to retrieve email.')
        return buildResponse(500, {'Message': 'Internal Server Error', 'Error': str(e)})

def saveEmail(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)
    except Exception as e:
        logger.exception('Unable to save user information.')
        return buildResponse(500, {'Message': 'Internal Server Error', 'Error': str(e)})

def modifyEmail(email, updateKey, updateValue):
    try:
        response = table.update_item(
            Key={'email': email},
            UpdateExpression='set %s = :value' % updateKey,
            ExpressionAttributeValues={':value': updateValue},
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    except Exception as e:
        logger.exception('Unable to update user information.')
        return buildResponse(500, {'Message': 'Internal Server Error', 'Error': str(e)})

def deleteEmail(email):
    try:
        response = table.delete_item(Key={'email': email}, ReturnValues='ALL_OLD')
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200, body)
    except Exception as e:
        logger.exception('Unable to delete account.')
        return buildResponse(500, {'Message': 'Internal Server Error', 'Error': str(e)})

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response

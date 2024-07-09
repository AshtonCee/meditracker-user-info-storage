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


def lambda_handler (event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    if httpMethod == getMethod and path == emailPath:
        response = getEmail(event['queryStringParameters']['email'])
    elif httpMethod == postMethod and path == emailPath:
        response = saveEmail(json.loads(event['body']))
    elif httpMethod == patchMethod and path == emailPath:
        requestBody = json.loads(event['body'])
        response = modifyEmail(requestBody['email'], requestBody['updateKey'], requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == emailPath:
        requestBody = json.loads(event['body'])
        response = deleteEmail(requestBody['email'])
    else:
        response = buildResponse(404, 'Not Found')

    return response

def getEmail(email):
    try:
        response = table.get_item(
            Key={
                'email': email
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'Email not found'})
    except:
        logger.exception('Unable to retrieve email.')

def saveEmail(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)
    except:
        logger.exception('Unable to save user information.')

def modifyEmail(email, updateKey, updateValue):
    try:
        response = table.update_item(
            Key={
                'email': email
            },
            UpdateExpression='set %s = :value' % updateKey,
            ExpressionAttributeValues={
                ':value': updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Unable to update user information.')

def deleteEmail(email):
    try:
        response = table.delete_item(
            Key={
                'email': email
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
    except:
        logger.exception('Unable to delete account.')
         

def buildResponse (statusCode, body=None):
    response = {
        'statusCode' : statusCode,
        'headers' : {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*' 
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response
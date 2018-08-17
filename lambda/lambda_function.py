from base64 import b64encode, b64decode
from hashlib import sha256
import hmac
import json
import os

import twitter
import boto3

ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME", "whereml")
SSM_CREDS_NAME = os.getenv("SSM_CREDS_NAME", "/twitter/whereml")
MAX_PREDICTIONS = os.getenv("MAX_PREDICTIONS", 3)
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/twitter/whereml")
ssm = boto3.client('ssm')
sagemaker = boto3.client('runtime.sagemaker')

CREDS = ssm.get_parameter(Name=SSM_CREDS_NAME)['Parameter']['Value'].split(',')
CONSUMER_SECRET = CREDS[1]
twitter_api = twitter.Api(*CREDS)
TWITTER_SN = twitter_api.VerifyCredentials().screen_name


def sign_crc(crc):
    h = hmac.new(bytes(CONSUMER_SECRET, 'ascii'), bytes(crc, 'ascii'), digestmod=sha256)
    return json.dumps({
        "response_token": "sha256="+b64encode(h.digest()).decode()
    })


def verify_request(event):
    crc = event['headers']['X-Twitter-Webhooks-Signature']
    h = hmac.new(bytes(CONSUMER_SECRET, 'ascii'), bytes(event['body'], 'utf-8'), digestmod=sha256)
    crc = b64decode(crc[7:])  # strip out the first 7 characters
    return hmac.compare_digest(h.digest(), crc)


def validate_record(tweet):
    if (
        TWITTER_SN.lower() in tweet.get('text', '').lower() and
        tweet.get('entities', {}).get('media') and
        'RT' not in tweet.get('text') and
        tweet['user']['screen_name'].lower() != TWITTER_SN.lower()
    ):
        return True
    return False
    

def lambda_handler(event, context):
    
    # deal with bad requests
    if event.get('path') != WEBHOOK_PATH:
        return {
            'statusCode': 404,
            'body': ''
        }
    
    # deal with subscription calls
    if event.get('httpMethod') == 'GET':
        crc = event.get('queryStringParameters', {}).get('crc_token')
        if not crc:
            return {
                'statusCode': 401,
                'body': 'bad crc'
            }
        return {
            'statusCode': 200,
            'body': sign_crc(crc)
        }
    
    # deal with bad crc
    if not verify_request(event):
        print("Unable to verify CRC")
        return {
            'statusCode': 400,
            'body': 'bad crc'
        }

    twitter_events = json.loads(event['body'])
    for tweet in twitter_events.get('tweet_create_events', []):
        media = tweet['entities']['media'][0]['media_url']
        if validate_record(tweet):
            results = json.loads(sagemaker.invoke_endpoint(
                EndpointName=ENDPOINT_NAME,
                Body=json.dumps({
                        'url': media,
                        'max_predictions': MAX_PREDICTIONS,
                        'rich': True
                    })
            )['Body'].read())
            status = results
            twitter_api.PostUpdate(
                "📍 ?\n" + status[0],
                media=status[1],
                in_reply_to_status_id=tweet['id_str'],
                auto_populate_reply_metadata=True
            )

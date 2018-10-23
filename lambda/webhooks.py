import boto3
from requests_oauthlib import OAuth1Session
ssm = boto3.client("ssm")
CREDS = ssm.get_parameter(Name=SSM_CREDS_NAME)['Parameter']['Value'].split(',')
twitter = OAuth1Session(CREDS)
api_url = "https://api.twitter.com/1.1/account_activity/all/env-beta/"

def create(webhook_url="https://api.whereml.bot/twitter/whereml"):
    twitter.post(
    	api_url+"webhooks.json",
    	params={'url': webhook_url}
    )

def subscribe():
    twitter.post(api_url+"subscriptions.json")

import json
import boto3

glue_client = boto3.client("glue")

def lambda_handler(event, context):
    messages = event['Records'][0]['Sns']['Message']
    print(messages)
    dmsEvent = json.loads(messages)
    if 'http://docs.aws.amazon.com/dms/latest/userguide/CHAP_Events.html#DMS-EVENT-0079' in dmsEvent['Event ID']:
        print('start crawler.')
        startCrawler()
    else:
        print("unknown message, ignore.")
    return {
        'statusCode': 200,
        'body': json.dumps('Task complete!')
    }

def startCrawler():
    crawler_name = "wmss3"
    try:
        # 启动AWS Glue Crawler
        response = glue_client.start_crawler(Name=crawler_name)
        return f"成功启动 AWS Glue Crawler: {crawler_name}"
    except Exception as e:
        return f"启动 AWS Glue Crawler 失败: {str(e)}"
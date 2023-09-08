import json
import re
import boto3
import urllib.parse

DatePattern = re.compile(r'\d\d\d\d')
s3 = boto3.resource('s3')
s3Client = boto3.client('s3');

def lambda_handler(event, context):
    # TODO implement
    print(event['Records']);
    
    affectedRecords = event['Records']
    for affectedRecord in affectedRecords:
        bucketName = affectedRecord['s3']['bucket']['name'];
        objectKey = affectedRecord['s3']['object']['key'];
        objectPrefix = objectKey[0: objectKey.rfind('/')]
        if DatePattern.search(objectPrefix):
            print('Record has date, Date=%s', objectKey)
        else:
            copy_source = {
                'Bucket': bucketName,
                'Key': objectKey
            }
            tagValue = getTagValue(bucketName, objectKey);
            date = '1970-01'
            if tagValue != 'None':
                date = tagValue[0:4]
            else: 
                print('tagValue is not right, %s,%s', bucketName, objectKey);
                break;
            
            fileName = objectKey.split('/')[-1];
            destinationKey = '/'.join(objectKey.split('/')[:-1]) + '/dttm=' + date + '/' + fileName;
            print('destinationKey:', destinationKey);
            s3.meta.client.copy(copy_source, bucketName, destinationKey);
            s3.Object(bucketName, destinationKey).wait_until_exists()
            s3.Object(bucketName, objectKey).delete();
            print('move data successfully destinationKey:', destinationKey);
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def getTagValue(bucketName, objectKey):
    # 获取对象标签
    response = s3Client.get_object_tagging(Bucket=bucketName, Key=objectKey);
    
    # 获取指定标签的值
    tag_value = None
    for tag in response['TagSet']:
        if tag['Key'] == 'dttm':
            tag_value = tag['Value']
            return tag_value;
            break
    return tag_value;

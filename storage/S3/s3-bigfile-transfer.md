# Cross border S3 big file transfer using s3 resumeable upload
- [S3 Big Files Transfer](#S3 big file transfer)
  - [1. onsideration](#consideration)
  - [2. Prepare environment](#prepare-environment)
    - [2.1 Launch EC2](#21-launch-ec2)
    - [2.2 Install Software](#22-install-the-following-softwareplugin-on-ec2)
  - [3. Configuration](#3-congiuration)
    - [3.1 Configure credentials](#31-configure-credentials)
    - [3.2 Download code repository](#32-download-the-code-repository)
    - [3.3 Configure transfer job](#33-change-the-transfer-config-file-for-your-job)
  - [4. Start the transfer job](#4-start-the-transfer-job)
## 1. Consideration
When you upload large files to Amazon S3, it's a best practice to leverage multipart uploads. If you're using the AWS Command Line Interface (AWS CLI), then all high-level aws s3 commands automatically perform a multipart upload when the object is large. These high-level commands include aws s3 cp and aws s3 sync.

In order to improve the quality and efficiency of uploads, you need to add breakpoint resume supported for large files.

In this case, we will transfer 1.5TiB AMI from AWS global region to China Regions using [amazon-s3-resumable-upload](https://github.com/aws-samples/amazon-s3-resumable-upload/blob/master/single_node)

## 2. Prepare environment
### 2.1 Launch EC2
Setup EC2 with Amazon Linux 2, Instance Type: m6i.2xlarge in one of the public subnet or private subnet with NAT in singapore region, and then login into the EC2.

### 2.2 Install the following software/plugin on EC2.
    python3
    boto3(AWS SDK)
    git
    Enable TCP BBR
- bash code
```bash
#!/bin/bash -v
sudo su
yum update -y
yum install git -y
yum install python3 -y
pip3 install boto3

# Setup BBR
echo "Setup BBR"
cat <<EOF>> /etc/sysconfig/modules/tcpcong.modules
#!/bin/bash
exec /sbin/modprobe tcp_bbr >/dev/null 2>&1
exec /sbin/modprobe sch_fq >/dev/null 2>&1
EOF
chmod 755 /etc/sysconfig/modules/tcpcong.modules
echo "net.ipv4.tcp_congestion_control = bbr" >> /etc/sysctl.d/00-tcpcong.conf
modprobe tcp_bbr
modprobe sch_fq
sysctl -w net.ipv4.tcp_congestion_control=bbr

```

## 3. Congiuration
### 3.1. Configure credentials
Create the credentials for China regions, and Global regions with following contents or following the [cli credential configuration](https://docs.aws.amazon.com/cli/latest/reference/configure/index.html).
```
vim ~/.aws/credentials
```

```
[china]
aws_access_key_id = REPLACE_WITH_CHINA_AK
aws_secret_access_key = REPLACE_WITH_CHINA_SK

[global]
aws_access_key_id = REPLACE_WITH_GLOBAL_AK
aws_secret_access_key = REPLACE_WITH_GLOBAL_SK
```

vim ~/.aws/config
```

```
[profile china]
region = cn-northwest-1
output = json

[profile global]
region = ap-southeast-1
output = json
```

### 3.2. Download the code repository.
```bash

echo "Download application amazon-s3-resumable-upload.git"
git clone https://github.com/aws-samples/amazon-s3-resumable-upload
cd amazon-s3-resumable-upload/single_node/
```

### 3.3. Configure transfer job
Change the transfer config file for your job.
- Update 
```bash

[Basic]
JobType = S3_TO_S3
# 'LOCAL_TO_S3' | 'S3_TO_S3' | 'ALIOSS_TO_S3'

DesProfileName = REPLACE_WITH_CHINA_PROFILE
# Profile name config in ~/.aws credentials. It is the destination account profile.
# 在~/.aws 中配置的能访问目标S3的 profile name

DesEndPointURL = AWS
# by default AWS S3 endpoint or other vendor's url e.g. https://storage.googleapis.com

DesBucket = REPLACE_THE_CHINA_ACCOUNT_BUCKET
# Destination S3 bucket name
# 目标文件bucket, type = str

S3Prefix =
# S3_TO_S3 mode Src. S3 Prefix, and same as Des. S3 Prefix; LOCAL_TO_S3 mode, this is Des. S3 Prefix.
# S3_TO_S3 源S3的Prefix(与目标S3一致)，LOCAL_TO_S3 则为目标S3的Prefix, type = str

SrcFileIndex = REPLACE_WITH_TRANSFER_FILE_NAME_IN_SOURCE_BUCKET
# Specify the file name to upload. Wildcard "*" to upload all.
# 指定要上传的文件的文件名, type = str，Upload全部文件则用 "*"

[LOCAL_TO_S3]
SrcDir = /home/ec2-user/mydir
# Source file directory. It is useless in S3_TO_S3 mode
# 原文件本地存放目录，S3_TO_S3 则该字段无效 type = str

[S3_TO_S3]
SrcProfileName = REPLACE_WITH_GLOBAL_PROFILE_NAME
# Profile name config in ~/.aws credentials. It is the source account profile. Useless for LOCAL_TO_S3 mode.
# 在~/.aws 中配置的能访问源S3的 profile name，LOCAL_TO_S3 则本字段无效

SrcEndPointURL = AWS
# by default AWS S3 endpoint or other vendor's url e.g. https://storage.googleapis.com

SrcBucket = REPLACE_WITH_SOURCE_BUCKET_NAME
# Source bucket name. It is useless in LOCAL_TO_S3 mode.
# 源Bucket，LOCAL_TO_S3 则本字段无效

[Advanced]
ChunkSize = 512
# File chunksize, unit MBytes, not less than 5MB. Single file parts number < 10,000, limited by S3 mulitpart upload API. The application will auto change it adapting to file size, you don't need to change it.
# 文件分片大小，单位为MB，不小于5M，单文件分片总数不能超过10000, 所以程序会根据文件大小自动调整该值，你一般无需调整。type = int

MaxRetry = 20
# Max retry times while S3 API call fail.
# S3 API call 失败，最大重试次数, type = int

MaxThread = 20
# Max threads for ONE file.
# 单文件同时上传的进程数量, type = int

MaxParallelFile = 5
# Max paralle running file, i.e. concurrency threads = MaxParallelFile * MaxThread
# 并行操作文件数量, type = int, 即同时并发的进程数 = MaxParallelFile * MaxThread

StorageClass = STANDARD
# 'STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE'

ifVerifyMD5 = False
```

## 4. Start the transfer job
Start the transfer job and check logs.
```bash
nohup python3 s3_upload.py &
tail -f nohup.out
```


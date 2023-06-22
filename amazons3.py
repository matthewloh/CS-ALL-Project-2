import boto3
from dotenv import load_dotenv
load_dotenv()
BUCKET_NAME = "csprojectbucket"

s3 = boto3.client('s3')

# List all buckets
# response = s3.list_buckets()

# for bucket in response['Buckets']:
#     print(bucket)

# List all objects in a bucket

# Upload a file to a bucket
# with open("Assets\holyplaceholder.png", "rb") as f:
#     s3.upload_fileobj(
#         f, BUCKET_NAME, "test_upload_1.png",
#     )
# response = s3.list_objects_v2(Bucket=BUCKET_NAME)
# for obj in response['Contents']:
#     # print(obj['Key'])
#     print(obj)

# Download a file from a bucket
# s3.download_file(BUCKET_NAME, "unknown-515.png", "downloaded_dog.png")

# Download file with binary data
# with open("downloaded_dog.png", "wb") as f:
#     s3.download_fileobj(BUCKET_NAME, "unknown-515.png", f)
#     # Code here to send image to frontend

# Getting a Presigned URL to Give Limited Access to an unauthorized user
# url = s3.generate_presigned_url("get_object", Params={
#     "Bucket": BUCKET_NAME, "Key": "unknown-515.png"}, ExpiresIn=60
#     )
# print(url)
# # Getting a Presigned URL to let unauthorized user upload a file
# url = s3.generate_presigned_url(ClientMethod="put_object", Params={
#     "Bucket": BUCKET_NAME, "Key": "test_upload_default_access.png"}, ExpiresIn=60
#     )
# print(url)

# with open("./Assets/holyplaceholder.png", "rb") as f:
#     s3.upload_fileobj(f, BUCKET_NAME, "test_upload_default_access.png")
video_url = s3.generate_presigned_url("get_object", Params={
    "Bucket": BUCKET_NAME, "Key": "Bad_Apples_Among_Us.mp4"}, ExpiresIn=600)
print(video_url)
# Create a Bucket
# bucket_location = s3.create_bucket(Bucket="new_bucket_777")
# print(bucket_location)

# Copy an object from one bucket to another
# s3.copy_object(
#     ACL="public-read",
#     Bucket="new_bucket_777",
#     CopySource=f"/{BUCKET_NAME}/unknown-515.png",
#     Key="unknown-515_copied.png",
# )

# Get an object's metadata
# response = s3.head_object(Bucket=BUCKET_NAME, Key="unknown-515.png")
# print(response)
# response = s3.get_object(Bucket=BUCKET_NAME, Key="unknown-515.png")
# print(response)

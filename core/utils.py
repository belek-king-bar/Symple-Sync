import boto3

from project.settings import AWS_STORAGE_BUCKET_NAME


def store_to_s3(path,file_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(AWS_STORAGE_BUCKET_NAME)
    bucket.upload_file(path, file_name)
    location = boto3.client('s3').get_bucket_location(Bucket=AWS_STORAGE_BUCKET_NAME)['LocationConstraint']
    url = "https://s3-%s.amazonaws.com/%s/%s" % (location, AWS_STORAGE_BUCKET_NAME, file_name)
    return url
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
from src.logs import logger

aws_access_key_id = ''
aws_secret_access_key = ''
aws_region = ''


# create an S3 client
s3 = boto3.client('s3', region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

def get_previous_month_filename():
    # Get the current date
    current_date = datetime.now()
    
    # Calculate the previous month's date
    previous_month_date = current_date - timedelta(days=current_date.day)
    
    # Format the date as "YYYY-MM"
    formatted_previous_month = previous_month_date.strftime("%Y-%m")
    
    # Create the result filename
    result_filename = formatted_previous_month + "-descriptions" + ".csv"
    
    return result_filename

result_filename = get_previous_month_filename()

#s3 definitions
bucket_name = 'domaindescriptions' #bucket
s3_object_key = result_filename #path within the S3 bucket.


def df_s3_prep(df): 
    csv_string = df.to_csv(index=False)
    return csv_string


def load_s3(csv_string):
    try:
        s3.put_object(Bucket=bucket_name, Key=s3_object_key, Body=csv_string)
        return {'success': True, 'message': 'Upload successful'}
    except ClientError as e:
        return {'success': False, 'message': f'Upload failed: {e}'}


def run_load_s3(df):
    logger.info('Uploading to s3...')
    data = df_s3_prep(df)
    load_s3(data)
    logger.info('Upload complete')


import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from datetime import datetime, timedelta







def generate_presigned_url(file_name, file_type=None, expiration=3600):
    """
    Generate a pre-signed URL for uploading a file to S3.
    
    :param file_name: The name of the file to upload (e.g., "image.jpg")
    :param file_type: Optional, the MIME type of the file (e.g., "image/jpeg")
    :param expiration: The expiry time of the pre-signed URL in seconds (default is 1 hour)
    :return: A tuple with the pre-signed URL and the S3 file key, or None if there was an error
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    try:
        # Define the S3 key (path) where the file will be stored
        file_key = f"uploads/{file_name}"

        # Generate the pre-signed URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_key,
                'ContentType': file_type or 'application/octet-stream',
            },
            ExpiresIn=expiration
        )

        # Return the pre-signed URL and file key
        return presigned_url, file_key

    except ClientError as e:
        print(f"Error generating pre-signed URL: {e}")
        return None, None




def split_availability(date, start_time, duration, interval_minutes=30):
    start = datetime.combine(date, start_time)
    slots = []
    total_minutes = duration['hours'] * 60 + duration['minutes']
    end_time = start + timedelta(minutes=total_minutes)

    while start < end_time:
        # Create slot for the current interval
        slot = {
            "date": start.date(),
            "start_time": start.time(),
            "duration": interval_minutes,  # Each interval in minutes
            "is_booked": False,
            "employee_id": "df14a9d7-1698-4c3f-a926-cf9c29224536",
            "is_unavailable": False,
        }
        slots.append(slot)

        # Move to the next interval
        start += timedelta(minutes=interval_minutes)
    
    return slots

import json
import boto3
import pandas as pd
import io

# Initialize S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Retrieve bucket name and file name from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']

    # Download the CSV file from S3
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        body = obj['Body'].read()
    except Exception as e:
        print(f"Error downloading file: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error downloading file')
        }

    # Read the CSV file into a DataFrame
    try:
        df = pd.read_csv(io.BytesIO(body))
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error reading CSV file: {str(e)}")
        }

    # Remove duplicate rows
    df_clean = df.drop_duplicates()
    # Remove rows with any missing values
    df_clean = df_clean.dropna()

    # Save the cleaned DataFrame as a CSV in memory
    processed_file_name = 'processed_' + file_name
    csv_buffer = io.StringIO()
    df_clean.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    # Upload the cleaned file back to S3
    try:
        s3_client.put_object(Bucket=bucket_name, Key=processed_file_name, Body=csv_buffer.getvalue())
        print(f"File {processed_file_name} successfully uploaded to S3.")
    except Exception as e:
        print(f"Error uploading the processed file to S3: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error uploading the processed file to S3: {str(e)}")
        }

    return {
        'statusCode': 200,
        'body': json.dumps(f'File {processed_file_name} processed and successfully uploaded to S3.')
    }

import datetime
from google.cloud import storage

def upload_to(instance, filename):
    
    date = str(datetime.datetime.now()).replace('.','_').replace(' ','_')
    url = 'files/file_' + date + filename
    return(url)


def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """ Upload data to a bucket"""
     
    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json(
        'credentials.json')

    #print(buckets = list(storage_client.list_buckets())

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(path_to_file)

    for blob in storage_client.list_blobs(bucket_name):
        print(str(blob))
    
    #returns a public url
    return blob.public_url
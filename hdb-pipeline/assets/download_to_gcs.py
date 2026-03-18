"""@bruin
name: download_to_gcs
image: python:3.13
secrets:
    - key: gcs
@bruin"""

import json
import os
import requests
from dotenv import find_dotenv, load_dotenv
from google.cloud import storage
from google.oauth2 import service_account

load_dotenv(find_dotenv())

# --- Config ---
DATASET_ID = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
INITIATE_URL = f"https://api-open.data.gov.sg/v1/public/api/datasets/{DATASET_ID}/initiate-download"
API_KEY = os.environ["DATAGOVSG_API_KEY"]
HEADERS = {"Authorization": API_KEY}

GCS_PATH = "datagovsg/ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv"

# Parse GCS connection injected by Bruin
gcs_conn = json.loads(os.environ["gcs"])
GCS_BUCKET = gcs_conn["bucket_name"]
SERVICE_ACCOUNT_FILE = gcs_conn["service_account_file"]


def get_download_url() -> str:
    resp = requests.get(INITIATE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()["data"]["url"]


def download_csv(url: str) -> bytes:
    print("Downloading CSV ...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    print(f"Downloaded {len(resp.content):,} bytes")
    return resp.content


def upload_to_gcs(data: bytes) -> None:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE
    )
    client = storage.Client(credentials=credentials)
    blob = client.bucket(GCS_BUCKET).blob(GCS_PATH)
    blob.upload_from_string(data, content_type="text/csv")
    print(f"Uploaded to gs://{GCS_BUCKET}/{GCS_PATH}")


print("Initiating download from data.gov.sg ...")
url = get_download_url()
data = download_csv(url)
upload_to_gcs(data)

"""
Download HDB resale flat price data from data.gov.sg and upload to GCS.

Usage:
    python download_resale_data.py

Requirements:
    pip install requests google-cloud-storage python-dotenv
"""

import os
import requests
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# --- Config ---
DATASET_ID = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
INITIATE_URL = f"https://api-open.data.gov.sg/v1/public/api/datasets/{DATASET_ID}/initiate-download"
API_KEY = os.environ["DATAGOVSG_API_KEY"]
HEADERS = {"Authorization": API_KEY}

GCS_BUCKET = "dsai-m2-bucket"
GCS_PATH = "datagovsg/ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv"
SERVICE_ACCOUNT_FILE = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/Users/ian/Documents/Keys/ntu-dsai-gcs-user.json",
)


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


def main():
    print("Initiating download from data.gov.sg ...")
    url = get_download_url()
    data = download_csv(url)
    upload_to_gcs(data)


if __name__ == "__main__":
    main()

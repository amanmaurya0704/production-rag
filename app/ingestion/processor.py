import os
import logfire
import json
import sys
import uuid
import vertexai


from typing import List
from google.cloud import storage
from qdrant_client import QdrantClient
from qdrant_client.http import models 

from app.config import settings
from app.services.retrieval.embedding import embed_text
from app.ingestion.loaders.pdf import parse_pdf
from app.ingestion.loaders.office import parse_office
from app.ingestion.loaders.text import parse_text
from app.ingestion.loaders.html import parse_html
from app.ingestion.chunking.splitter import chunk_text


logfire.configure( service_name ="ingestion-processor")

vertexai.init(project=settings.PROJECT_ID, location = settings.LOCATION)

storage_client = storage.Client(project=settings.PROJECT_ID)

qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

def upload_to_gcs(data, bucket_name:str, destination_blob_name:str, is_json:bool = False):
    """
    Uploads data to Google Cloud Storage.

    Args:
        data (bytes): The data to upload.
        bucket_name (str): The name of the GCS bucket.
        destination_blob_name (str): The destination path in the bucket.
    """
    with logfire.span("Uploading to GCS", bucket=bucket_name, destination=destination_blob_name):
        try:
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            if is_json:
                blob.upload_from_string(json.dumps(data), content_type='application/json')
            else:
                blob.upload_from_string(data)
            logfire.info(f"Data uploaded to GCS at {destination_blob_name}")
        except Exception as e:
            logfire.error(f"Error uploading to GCS: {e}")
            raise e

def _ensure_collection():
    if not qdrant_client.collection_exists(settings.QDRANT_COLLECTION):
        qdrant_client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )
        logfire.info(f"🆕 Created Qdrant collection '{settings.QDRANT_COLLECTION}'")

def process_file(file_path:str, filename: str, source_type: str,skip_raw_upload: bool = False):
    """
    Processes a file based on its source type, extracts text, chunks it, and uploads to GCS.

    Args:
        file_path (str): The path to the file.
        filename (str): The name of the file.
        source_type (str): The type of the source (e.g., 'pdf', 'docx', 'txt', 'html').
    """
    with logfire.span("Processing file", filename=filename, source_type=source_type):
        try:
            raw_gcs_path = f"{source_type}/{filename}"
            if not skip_raw_upload:
                upload_to_gcs(file_path, settings.RAW_BUCKET, raw_gcs_path)
            else:
                logfire.info(f"⏩ Skipping RAW upload (cloud mode) — file already at gs://{settings.RAW_BUCKET}/{raw_gcs_path}")

            

            ext = filename.lower().split('.')[-1]
            if ext == "pdf":
                full_text = parse_pdf(file_path)
            elif ext in ["docx", "pptx"]:
                full_text = parse_office(file_path)
            elif ext == "txt":
                full_text = parse_text(file_path)
            elif ext in ["html", "htm"]:
                full_text = parse_html(file_path)
            else:
                logfire.warning(f"Unsupported file extension: {ext}. Skipping processing.")
                return
            
            if not full_text or not full_text.strip():
                logfire.warning(f"File {filename} contains no readable text. Skipping processing.")
                return

            chunks = chunk_text(full_text)
            if not chunks:
                return
            
            processed_data = {"filename": filename, "chunks": chunks}
            processed_gcs_path = f"{source_type}/{filename}.json"
            upload_to_gcs(processed_data, settings.PROCESSED_BUCKET, processed_gcs_path, is_json=True)

            with logfire.span("Vectorizing and indexing"):
                embeddings = embed_text(chunks)
                points = [
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "text": chunk,
                            "source": filename,
                            "source_type": source_type,
                            "raw_gcs_path": f"gs://{settings.RAW_BUCKET}/{raw_gcs_path}",
                        },
                    )
                    for chunk, vector in zip(chunks, embeddings)
                ]

                qdrant_client.upsert(
                    collection_name=settings.QDRANT_COLLECTION,
                    points=points,
                )

                logfire.info(f"✨ Indexed {len(points)} points to Qdrant from '{filename}'")


            logfire.info(f"File {filename} processed and uploaded successfully.")
        except Exception as e:
            logfire.error(f"Error processing file {filename}: {e}")
            raise e

def run_universal_ingestion(base_dir: str, explicit_source_type: str = None, wipe: bool = False):
    """
    CLI entry point — scans a local directory, uploads files to RAW bucket, then processes.
    """
    with logfire.span("🌍 Universal Ingestion Started", base_directory=base_dir):
        if wipe:
            with logfire.span("🧹 Wiping Collection"):
                if qdrant_client.collection_exists(settings.QDRANT_COLLECTION):
                    qdrant_client.delete_collection(settings.QDRANT_COLLECTION)
                    logfire.info(f"🗑️ Collection '{settings.QDRANT_COLLECTION}' deleted")

        _ensure_collection()

        subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

        if not subdirs:
            if explicit_source_type:
                source_type = explicit_source_type
            else:
                base_name   = os.path.basename(os.path.normpath(base_dir)).lower()
                source_type = "true" if "true" in base_name else "noisy" if "noisy" in base_name else "general"
            logfire.info(f"📂 No subdirectories — processing {base_dir} as '{source_type}'")
            _process_directory(base_dir, source_type)
        else:
            for subdir in subdirs:
                source_type = "true" if "true" in subdir.lower() else "noisy" if "noisy" in subdir.lower() else subdir
                _process_directory(os.path.join(base_dir, subdir), source_type)

def _process_directory(dir_path: str, source_type: str):

    with logfire.span("📁 Scanning Directory", path=dir_path, source=source_type):
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        logfire.info(f"🔍 Found {len(files)} files")
        for filename in files:
            process_file(os.path.join(dir_path, filename), filename, source_type, skip_raw_upload=False)


if __name__ == "__main__":
    wipe_requested = "--wipe" in sys.argv
    clean_args     = [a for a in sys.argv if a != "--wipe"]
    target_dir     = clean_args[1] if len(clean_args) > 1 else "DATA"
    explicit_type  = clean_args[2] if len(clean_args) > 2 else None

    if not os.path.exists(target_dir):
        print(f"Error: Path {target_dir} does not exist.")
        sys.exit(1)

    run_universal_ingestion(target_dir, explicit_source_type=explicit_type, wipe=wipe_requested)
    logfire.info("🏁 Universal Ingestion Job Completed")
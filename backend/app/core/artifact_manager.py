import os
import boto3
import joblib
import json
import logging
from io import BytesIO
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArtifactManager:
    def __init__(self):
        self.mode = os.getenv("ARTIFACT_STORAGE_MODE", "LOCAL")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        # Initialize S3 client only if in S3 mode
        if self.mode == "S3":
            try:
                self.s3_client = boto3.client(
                    's3',
                    region_name=os.getenv("AWS_REGION", "us-east-1"),
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                )
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                raise

    def save_model(self, series_id, model_object, manifest_dict):
        try:
            if self.mode == "LOCAL":
                # Save to ml/models/ folder
                joblib.dump(model_object, f"ml/models/{series_id}.pkl")
                with open(f"ml/models/{series_id}.json", "w") as f:
                    json.dump(manifest_dict, f)
            elif self.mode == "S3":
                # Serialize model to memory buffer
                model_buffer = BytesIO()
                joblib.dump(model_object, model_buffer)
                model_buffer.seek(0)
                # Upload model to S3
                self.s3_client.upload_fileobj(
                    model_buffer,
                    Bucket=self.bucket_name,
                    Key=f"models/{series_id}.pkl"
                )
                # Serialize and upload manifest
                manifest_buffer = BytesIO(json.dumps(manifest_dict).encode('utf-8'))
                self.s3_client.upload_fileobj(
                    manifest_buffer,
                    Bucket=self.bucket_name,
                    Key=f"models/{series_id}.json"
                )
        except ClientError as e:
            logger.error(f"S3 upload failed for {series_id}: {e}")
            raise
        except (IOError, OSError) as e:
            logger.error(f"File operation failed for {series_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving model {series_id}: {e}")
            raise

    def load_model(self, series_id):
        try:
            if self.mode == "LOCAL":
                return joblib.load(f"ml/models/{series_id}.pkl")
            elif self.mode == "S3":
                # Download model to memory buffer
                buffer = BytesIO()
                self.s3_client.download_fileobj(
                    Bucket=self.bucket_name,
                    Key=f"models/{series_id}.pkl",
                    Fileobj=buffer
                )
                buffer.seek(0)
                return joblib.load(buffer)
        except ClientError as e:
            logger.error(f"S3 download failed for {series_id}: {e}")
            raise
        except (IOError, OSError) as e:
            logger.error(f"File operation failed for {series_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading model {series_id}: {e}")
            raise
    
    def load_manifest(self, series_id):
        """Retrieves the manifest JSON (metadata) for a model."""
        try:
            if self.mode == "LOCAL":
                # Match the naming convention used in save_model ({series_id}.json)
                path = f"ml/models/{series_id}.json"
                with open(path, 'r') as f:
                    return json.load(f)
            elif self.mode == "S3":
                buffer = BytesIO()
                self.s3_client.download_fileobj(
                    Bucket=self.bucket_name,
                    Key=f"models/{series_id}.json",
                    Fileobj=buffer
                )
                buffer.seek(0)
                return json.loads(buffer.read().decode('utf-8'))
        except Exception as e:
            logger.error(f"Error loading manifest {series_id}: {e}")
            raise
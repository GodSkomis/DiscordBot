import json
import logging
import os

from contextlib import asynccontextmanager
from typing import Dict, Self

from aiobotocore.session import get_session
from botocore.exceptions import ClientError

from settings import BASE_PATH, S3_CONF_FILE_NAME, S3_BOt_TOKEN_FILE_NAME


class S3Client:
    _instance: Self = None
    
    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        data = self._read_config()
        self.config = {
            "region_name": data['region_name'],
            "aws_access_key_id": data['access_key'],
            "aws_secret_access_key": data['secret_key'],
        }
        self.bucket_name = data['bucket_name']
        self.session = get_session()

    def _read_config(self) -> Dict[str, str]:
        with open(os.path.join(BASE_PATH, S3_CONF_FILE_NAME), 'r') as file:
            data = json.load(file)
        if not data:
            raise ValueError("S3 configuration not found")
        return data

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    # async def upload_file(
    #         self,
    #         file_path: str,
    # ):
    #     object_name = file_path.split("/")[-1]
    #     try:
    #         async with self.get_client() as client:
    #             with open(file_path, "rb") as file:
    #                 await client.put_object(
    #                     Bucket=self.bucket_name,
    #                     Key=object_name,
    #                     Body=file,
    #                 )
    #             print(f"File {object_name} uploaded to {self.bucket_name}")
    #     except ClientError as e:
    #         print(f"Error uploading file: {e}")

    # async def delete_file(self, object_name: str):
    #     try:
    #         async with self.get_client() as client:
    #             await client.delete_object(Bucket=self.bucket_name, Key=object_name)
    #             print(f"File {object_name} deleted from {self.bucket_name}")
    #     except ClientError as e:
    #         print(f"Error deleting file: {e}")

    # async def get_file(self, object_name: str, destination_path: str):
    #     try:
    #         async with self.get_client() as client:
    #             response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
    #             data = await response["Body"].read()
    #             with open(destination_path, "wb") as file:
    #                 file.write(data)
    #             print(f"File {object_name} downloaded to {destination_path}")
    #     except ClientError as e:
    #         print(f"Error downloading file: {e}")

    async def get_bot_token(self):
        async with self.get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=S3_BOt_TOKEN_FILE_NAME)
            data = (await response["Body"].read()).decode('utf-8')
            logging.info('BOT TOKEN HAVE BEE LOADED SUCCESSFULY')
            return data

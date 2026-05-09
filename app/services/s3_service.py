import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)


class S3Service:
    @staticmethod
    def upload_file(file_obj, file_name: str, content_type: str):

        try:
            s3_client.upload_fileobj(
                file_obj,
                settings.aws_s3_bucket,
                file_name,
                ExtraArgs={
                    "ContentType": content_type
                }
            )

            return (
                f"https://{settings.aws_s3_bucket}.s3."
                f"{settings.aws_region}.amazonaws.com/{file_name}"
            )

        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")
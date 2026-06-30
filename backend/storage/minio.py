from minio import Minio

from config import env


client = Minio(
    endpoint=env.MINIO_ENDPOINT,
    access_key=env.MINIO_ACCESS_KEY,
    secret_key=env.MINIO_SECRET_KEY,
    secure=env.MINIO_SECURE
)


def create_bucket_if_not_exists() -> None:
    if not client.bucket_exists(env.MINIO_BUCKET):
        client.make_bucket(env.MINIO_BUCKET)

def delete_object(object_name: str) -> None:
    client.remove_object(
        env.MINIO_BUCKET,
        object_name
    )
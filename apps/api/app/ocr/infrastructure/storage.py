"""Private Azure Blob and Queue Storage adapter; Azurite uses the same API."""

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.storage.queue import QueueServiceClient

from app.config import settings


def _connection_string() -> str:
    return settings.storage_connection_string


def _blob_service() -> BlobServiceClient:
    # Pin a version supported by both Azure Storage and current Azurite.
    return BlobServiceClient.from_connection_string(_connection_string(), api_version="2023-11-03")


def _queue_service() -> QueueServiceClient:
    return QueueServiceClient.from_connection_string(_connection_string(), api_version="2023-11-03")


def _ensure_container(client) -> None:
    try:
        client.create_container()
    except ResourceExistsError:
        pass


def _ensure_queue(client) -> None:
    try:
        client.create_queue()
    except ResourceExistsError:
        pass


def upload_screenshot(object_key: str, payload: bytes) -> None:
    container = _blob_service().get_container_client(settings.ocr_container_name)
    _ensure_container(container)
    container.upload_blob(object_key, payload, overwrite=False, content_settings=ContentSettings(content_type="image/png"))


def download_screenshot(object_key: str) -> bytes:
    return _blob_service().get_blob_client(settings.ocr_container_name, object_key).download_blob().readall()


def delete_screenshot(object_key: str) -> None:
    from azure.core.exceptions import ResourceNotFoundError

    try:
        _blob_service().get_blob_client(settings.ocr_container_name, object_key).delete_blob(delete_snapshots="include")
    except ResourceNotFoundError:
        pass


def enqueue_job(job_id: str) -> None:
    queue = _queue_service().get_queue_client(settings.ocr_queue_name)
    _ensure_queue(queue)
    queue.send_message(job_id, time_to_live=86_400)


def get_queue_client():
    queue = _queue_service().get_queue_client(settings.ocr_queue_name)
    _ensure_queue(queue)
    return queue

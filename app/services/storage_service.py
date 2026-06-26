"""Servico de armazenamento de arquivos usando MinIO/S3 compatible."""
import base64
from datetime import datetime
import uuid

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings


class StorageServiceError(RuntimeError):
    """Erro controlado para falhas de storage."""


class StorageService:
    """Servico para upload de arquivos no MinIO Storage via S3."""

    def __init__(self):
        self.s3_client = None
        self.bucket = settings.MINIO_BUCKET
        self.public_url = settings.MINIO_PUBLIC_URL.rstrip("/")

    def _get_client(self):
        """Inicializa o cliente S3 sob demanda."""
        if self.s3_client is not None:
            return self.s3_client

        if not settings.MINIO_ENDPOINT or not settings.MINIO_ACCESS_KEY or not settings.MINIO_SECRET_KEY:
            raise StorageServiceError("Storage nao configurado. Verifique as variaveis MINIO_*.")

        protocol = "https" if settings.MINIO_SECURE else "http"
        endpoint_url = f"{protocol}://{settings.MINIO_ENDPOINT}"

        try:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                config=Config(signature_version="s3v4"),
                region_name="us-east-1",
            )
        except (BotoCoreError, ClientError) as exc:
            raise StorageServiceError(f"Erro ao inicializar storage: {exc}") from exc

        return self.s3_client

    def _ensure_bucket_exists(self):
        """Cria o bucket se ele nao existir."""
        client = self._get_client()

        try:
            client.head_bucket(Bucket=self.bucket)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code not in ("404", "NoSuchBucket", "NotFound"):
                raise StorageServiceError(f"Erro ao acessar bucket '{self.bucket}': {exc}") from exc

            try:
                client.create_bucket(Bucket=self.bucket)
                print(f"[MinIO] Bucket '{self.bucket}' criado com sucesso")
            except (BotoCoreError, ClientError) as create_exc:
                raise StorageServiceError(f"Erro ao criar bucket '{self.bucket}': {create_exc}") from create_exc
        except BotoCoreError as exc:
            raise StorageServiceError(f"Erro ao acessar storage: {exc}") from exc

    def _decode_base64(self, foto_base64: str) -> bytes:
        if "," in foto_base64:
            foto_base64 = foto_base64.split(",", 1)[1]

        try:
            return base64.b64decode(foto_base64, validate=True)
        except Exception as exc:
            raise StorageServiceError("Imagem base64 invalida.") from exc

    def _upload_image(
        self,
        foto_base64: str,
        filename: str,
        content_type: str,
    ) -> str:
        self._ensure_bucket_exists()
        foto_bytes = self._decode_base64(foto_base64)

        try:
            self._get_client().put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=foto_bytes,
                ContentType=content_type,
            )
        except (BotoCoreError, ClientError) as exc:
            raise StorageServiceError(f"Erro ao enviar arquivo para storage: {exc}") from exc

        return f"{self.public_url}/{self.bucket}/{filename}"

    def upload_presenca_foto(
        self,
        foto_base64: str,
        diaria_id: int,
        pessoa_id: int,
        content_type: str = "image/jpeg",
    ) -> str:
        """Faz upload de foto de presenca."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        extension = "jpg" if "jpeg" in content_type else "png"
        filename = f"presencas/diaria_{diaria_id}/pessoa_{pessoa_id}_{timestamp}_{unique_id}.{extension}"

        return self._upload_image(foto_base64, filename, content_type)

    def upload_perfil_foto(
        self,
        foto_base64: str,
        pessoa_id: int,
        content_type: str = "image/jpeg",
    ) -> str:
        """Faz upload de foto de perfil do usuario."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        extension = "jpg" if "jpeg" in content_type else "png"
        filename = f"perfis/pessoa_{pessoa_id}_{timestamp}_{unique_id}.{extension}"

        return self._upload_image(foto_base64, filename, content_type)

    def delete_file(self, file_path: str) -> bool:
        """Deleta um arquivo do bucket."""
        try:
            self._get_client().delete_object(Bucket=self.bucket, Key=file_path)
            return True
        except (BotoCoreError, ClientError, StorageServiceError) as exc:
            print(f"Erro ao deletar arquivo: {exc}")
            return False


# Instancia global leve: o cliente S3 e inicializado apenas no primeiro uso.
storage_service = StorageService()

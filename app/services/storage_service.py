"""
Serviço de armazenamento de arquivos usando MinIO (S3 Compatible).
"""
import boto3
from botocore.client import Config
import uuid
from datetime import datetime
import base64

from app.core.config import settings


class StorageService:
    """Serviço para upload de arquivos no MinIO Storage via S3."""

    def __init__(self):
        """Inicializa o cliente S3 para MinIO."""
        # Monta a URL do endpoint
        protocol = "https" if settings.MINIO_SECURE else "http"
        endpoint_url = f"{protocol}://{settings.MINIO_ENDPOINT}"
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'  # MinIO não usa região real
        )
        self.bucket = settings.MINIO_BUCKET
        self.public_url = settings.MINIO_PUBLIC_URL
        
        # Garante que o bucket existe
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Cria o bucket se não existir."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket)
                print(f"[MinIO] Bucket '{self.bucket}' criado com sucesso")
            except Exception as e:
                print(f"[MinIO] Aviso ao criar bucket: {e}")

    def upload_presenca_foto(
        self,
        foto_base64: str,
        diaria_id: int,
        pessoa_id: int,
        content_type: str = "image/jpeg"
    ) -> str:
        """
        Faz upload de foto de presença.
        
        Args:
            foto_base64: Imagem em base64
            diaria_id: ID da diária
            pessoa_id: ID da pessoa
            content_type: Tipo MIME da imagem
            
        Returns:
            URL pública da imagem
        """
        # Remove prefixo data:image/... se existir
        if ',' in foto_base64:
            foto_base64 = foto_base64.split(',')[1]
        
        # Decodifica base64
        foto_bytes = base64.b64decode(foto_base64)
        
        # Gera nome único para o arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        extension = 'jpg' if 'jpeg' in content_type else 'png'
        filename = f"presencas/diaria_{diaria_id}/pessoa_{pessoa_id}_{timestamp}_{unique_id}.{extension}"
        
        # Upload para o bucket
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=foto_bytes,
            ContentType=content_type,
        )
        
        # Retorna URL pública (MinIO)
        public_url = f"{self.public_url}/{self.bucket}/{filename}"
        return public_url

    def upload_perfil_foto(
        self,
        foto_base64: str,
        pessoa_id: int,
        content_type: str = "image/jpeg"
    ) -> str:
        """
        Faz upload de foto de perfil do usuário.
        
        Args:
            foto_base64: Imagem em base64
            pessoa_id: ID da pessoa
            content_type: Tipo MIME da imagem
            
        Returns:
            URL pública da imagem
        """
        # Remove prefixo data:image/... se existir
        if ',' in foto_base64:
            foto_base64 = foto_base64.split(',')[1]
        
        # Decodifica base64
        foto_bytes = base64.b64decode(foto_base64)
        
        # Gera nome único para o arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        extension = 'jpg' if 'jpeg' in content_type else 'png'
        filename = f"perfis/pessoa_{pessoa_id}_{timestamp}_{unique_id}.{extension}"
        
        # Upload para o bucket
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=foto_bytes,
            ContentType=content_type,
        )
        
        # Retorna URL pública (MinIO)
        public_url = f"{self.public_url}/{self.bucket}/{filename}"
        return public_url

    def delete_file(self, file_path: str) -> bool:
        """
        Deleta um arquivo do bucket.
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=file_path
            )
            return True
        except Exception as e:
            print(f"Erro ao deletar arquivo: {e}")
            return False


# Instância global do serviço
storage_service = StorageService()

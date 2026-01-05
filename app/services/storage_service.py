"""
Serviço de armazenamento de arquivos usando Supabase Storage (S3 Compatible).
"""
import boto3
from botocore.client import Config
import uuid
from datetime import datetime
import base64

from app.core.config import settings


class StorageService:
    """Serviço para upload de arquivos no Supabase Storage via S3."""

    def __init__(self):
        """Inicializa o cliente S3 para Supabase Storage."""
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.SUPABASE_STORAGE_URL,
            aws_access_key_id=settings.SUPABASE_STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.SUPABASE_STORAGE_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name=settings.SUPABASE_STORAGE_REGION
        )
        self.bucket = settings.SUPABASE_STORAGE_BUCKET
        self.project_url = settings.SUPABASE_PROJECT_URL

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
        
        # Retorna URL pública
        public_url = f"{self.project_url}/storage/v1/object/public/{self.bucket}/{filename}"
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
        
        # Retorna URL pública
        public_url = f"{self.project_url}/storage/v1/object/public/{self.bucket}/{filename}"
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

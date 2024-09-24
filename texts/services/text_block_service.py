from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import F

from texts.models import TextBlock
from texts.utils.s3_service import S3Service
from texts.utils_functions import generate_unique_hash
from texts.services.password_service import PasswordService


class TextBlockService:

    @staticmethod
    def create_text_block(content: str, expires_in: int, password: str = None):
        hash = generate_unique_hash()
        s3_key = f'{hash}.txt'
        content_bytes = content.encode('utf-8')
        content_file = ContentFile(content_bytes)

        storage = S3Service.get_storage()
        saved_filename = storage.save(s3_key, content_file)

        expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
        text_block = TextBlock.objects.create(
            hash=hash,
            s3_key=saved_filename,
            expires_at=expires_at
        )

        if password:
            hashed_password = PasswordService.hash_password(password)
            text_block.password = hashed_password
            text_block.save()

        return text_block

    @staticmethod
    def increment_views(url_token: str):
        return TextBlock.objects.filter(url_token=url_token).update(views=F('views') + 1)

    @staticmethod
    def get_text_block_by_token(url_token: str):
        try:
            return TextBlock.objects.get(url_token=url_token)
        except TextBlock.DoesNotExist:
            return None

    @staticmethod
    def delete_expired_text_block(text_block: TextBlock):
        if text_block.expires_at < timezone.now():
            text_block.delete()
            return True
        return False

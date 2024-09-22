from django.utils.module_loading import import_string
from django.conf import settings


class S3Service:
    @staticmethod
    def get_storage():
        StorageClass = import_string(settings.DEFAULT_FILE_STORAGE)
        return StorageClass()

    @staticmethod
    def read_file(s3_key):
        storage = S3Service.get_storage()
        with storage.open(s3_key, 'rb') as file_obj:
            return file_obj.read().decode('utf-8')

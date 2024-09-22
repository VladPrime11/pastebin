from django.views import View
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseServerError
from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import TextBlock
from .utils import generate_unique_hash


@method_decorator(csrf_exempt, name='dispatch')
class CreateTextBlockView(View):
    def post(self, request):
        content = request.POST.get('content')
        expires_in = request.POST.get('expires_in')

        if not content or not expires_in:
            return JsonResponse({'error': 'Поля content и expires_in обязательны.'}, status=400)

        try:
            expires_in = int(expires_in)
            if expires_in <= 0:
                raise ValueError
        except ValueError:
            return JsonResponse({'error': 'expires_in должно быть положительным целым числом.'}, status=400)

        hash = generate_unique_hash()
        s3_key = f'texts/{hash}.txt'
        content_bytes = content.encode('utf-8')
        content_file = ContentFile(content_bytes)

        StorageClass = import_string(settings.DEFAULT_FILE_STORAGE)
        storage = StorageClass()

        try:
            saved_filename = storage.save(s3_key, content_file)
        except Exception as e:
            return JsonResponse({'error': 'Ошибка при сохранении файла.'}, status=500)

        expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
        text_block = TextBlock.objects.create(
            hash=hash,
            s3_key=saved_filename,
            expires_at=expires_at
        )

        return JsonResponse({'hash': text_block.hash}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class RetrieveTextBlockView(View):
    def get(self, request, hash):
        try:
            text_block = TextBlock.objects.get(hash=hash)
        except TextBlock.DoesNotExist:
            return HttpResponseNotFound("Текстовый блок не найден.")

        if text_block.expires_at < timezone.now():
            text_block.delete()
            return HttpResponseNotFound("Текстовый блок истёк и был удалён.")

        StorageClass = import_string(settings.DEFAULT_FILE_STORAGE)
        storage = StorageClass()

        try:
            with storage.open(text_block.s3_key, 'rb') as file_obj:
                content = file_obj.read().decode('utf-8')
        except Exception as e:
            return HttpResponseServerError("Ошибка при получении контента.")

        text_block.views += 1
        text_block.save()

        return JsonResponse({'content': content})

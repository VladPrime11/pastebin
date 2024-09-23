from django.views import View
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from texts.services.text_block_service import TextBlockService
from texts.services.cache_service import CacheService
from texts.utils.s3_service import S3Service


@method_decorator(csrf_exempt, name='dispatch')
class CreateTextBlockView(View):
    def post(self, request):
        content = request.POST.get('content')
        expires_in = request.POST.get('expires_in')

        if not content or not expires_in:
            return JsonResponse({'error': 'The content and expires_in fields are mandatory.'}, status=400)

        try:
            expires_in = int(expires_in)
            if expires_in <= 0:
                raise ValueError
        except ValueError:
            return JsonResponse({'error': 'expires_in must be a positive integer.'}, status=400)

        try:
            text_block = TextBlockService.create_text_block(content, expires_in)
        except Exception as e:
            return JsonResponse({'error': 'Error when saving a file.'}, status=500)

        relative_url = reverse('retrieve_text_block', args=[text_block.url_token])
        full_url = request.build_absolute_uri(relative_url)

        return JsonResponse({'url': full_url}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class RetrieveTextBlockView(View):
    def get(self, request, url_token):
        cache_key = f"text_block_{url_token}"
        popular_cache_key = f"popular_text_block_{url_token}"
        min_views = 5

        cached_popular_data = CacheService.get_from_cache(popular_cache_key)
        if cached_popular_data:
            TextBlockService.increment_views(url_token)
            return JsonResponse(cached_popular_data)

        cached_data = CacheService.get_from_cache(cache_key)
        if cached_data:
            TextBlockService.increment_views(url_token)

            text_block = TextBlockService.get_text_block_by_token(url_token)
            if not text_block:
                return HttpResponseNotFound('Text block not found.')

            current_views = text_block.views
            cached_data['views'] = current_views
            CacheService.set_to_cache(cache_key, cached_data, 300)

            if current_views >= min_views:
                CacheService.set_to_cache(popular_cache_key, cached_data, 3000)

            return JsonResponse(cached_data)

        text_block = TextBlockService.get_text_block_by_token(url_token)
        if not text_block:
            return HttpResponseNotFound('Text block not found.')

        if TextBlockService.delete_expired_text_block(text_block):
            return HttpResponseNotFound('The text block expired and was deleted.')

        try:
            content = S3Service.read_file(text_block.s3_key)
        except Exception as e:
            return HttpResponseServerError('Error when retrieving content.')

        TextBlockService.increment_views(url_token)

        text_block.refresh_from_db()
        current_views = text_block.views

        data = {
            'content': content,
            'views': current_views,
            'created_at': text_block.created_at.isoformat(),
        }

        CacheService.set_to_cache(cache_key, data, 300)

        if current_views >= min_views:
            CacheService.set_to_cache(popular_cache_key, data, 3000)

        return JsonResponse(data)

import time
from django.http import JsonResponse
from django.core.cache import cache


class ThrottleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')

        key = f"throttle_{ip}_{time.strftime('%Y-%m-%d-%H')}"

        try:
            current_count = cache.get(key, 0)
            if current_count >= 5:
                return JsonResponse({'error': 'Too many requests'}, status=429)
            else:
                cache.set(key, current_count + 1, 5)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        response = self.get_response(request)

        return response
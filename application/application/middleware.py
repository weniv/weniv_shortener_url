class XForwardedForMiddleware:
    """프록시(Traefik)가 붙인 실제 접속 IP를 REMOTE_ADDR에 넣는다.

    X-Forwarded-For의 첫 값은 접속한 사람이 마음대로 보낼 수 있어 횟수 제한을 피하는 데 쓰인다.
    맨 끝 값은 바로 앞 프록시가 직접 본 주소라 바꿀 수 없으므로 그것을 쓴다.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
            if ip:
                request.META['REMOTE_ADDR'] = ip
        response = self.get_response(request)
        return response

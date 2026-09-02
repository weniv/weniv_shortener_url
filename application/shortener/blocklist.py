"""단축 대상 URL 차단 규칙.

스패머가 `https://s.click.al%69express.com/...` 처럼 호스트를 퍼센트 인코딩해
문자열 검사만 하는 필터를 우회하므로, 판정 전에 URL을 정규화한다.
"""
import re
from urllib.parse import urlsplit, unquote

from django.conf import settings

# 어필리에이트 스팸
SPAM_DOMAINS = {
    'aliexpress.com',
    'aliexpress.us',
    'aliexpress.ru',
    'aliexpress.co.kr',
}

# 다른 단축 URL 서비스 (체이닝으로 최종 목적지를 숨기는 데 쓰임)
SHORTENER_DOMAINS = {
    'ual.kr', 'iii.im', 'tny.kr', 'url.kr', 'buly.kr', 'zrr.kr', 'vo.la',
    'han.gl', 'muz.so', 'soo.gd', 'abit.ly',
    'bit.ly', 'bitly.com', 'tinyurl.com', 'is.gd', 'cutt.ly', 'shorturl.at',
    'rebrand.ly', 'rb.gy', 't.ly', 't.co', 'goo.gl', 's.id', 'shorturl.asia',
}

# 확인된 피싱 호스트 (Interac 사칭)
PHISHING_DOMAINS = {
    'lntpac.cfd', 'www-lnter-ca.cfd', 'web-lnter-ca.cfd', 'www-lnter-ca.top',
    'www-lnter-ca.live', 'web-interca-receive24link.cfd', 'intera-cad-id7642.shop',
    'einterac-id49307.cfd',
}

# 스팸/피싱 비율이 압도적으로 높은 TLD
BLOCKED_TLDS = {'cfd', 'sbs', 'cyou', 'icu', 'rest', 'monster', 'buzz', 'top'}


def _extra(name):
    """.env 에서 콤마로 구분해 추가 도메인을 넣을 수 있게 한다."""
    raw = getattr(settings, name, '') or ''
    return {d.strip().lower().lstrip('.') for d in raw.split(',') if d.strip()}


def blocked_domains(include_self=True):
    domains = (SPAM_DOMAINS | SHORTENER_DOMAINS | PHISHING_DOMAINS
               | _extra('EXTRA_BLOCKED_DOMAINS'))
    if include_self:
        # 자기 자신을 다시 단축하면 무한 루프가 되므로 생성 단계에서만 막는다.
        # 리다이렉트 단계에서는 기존에 만들어진 체인이 끊기지 않도록 허용한다.
        domains |= {settings.BASE_NAME.lower()}
    return domains


def blocked_tlds():
    return BLOCKED_TLDS | _extra('EXTRA_BLOCKED_TLDS')


def candidate_hosts(url: str) -> set:
    """퍼센트 인코딩을 단계적으로 풀어가며 나오는 호스트를 모두 수집한다.

    `al%69express.com` → `aliexpress.com`, `al%2569express.com` → 2단계 후 동일.
    """
    hosts = set()
    current = url or ''
    for _ in range(3):
        try:
            host = urlsplit(current).hostname or ''
        except ValueError:
            host = ''
        host = host.lower().rstrip('.')
        if host:
            hosts.add(host)
            # 국제화 도메인(퓨니코드)도 양쪽 표기를 모두 후보에 넣는다
            try:
                hosts.add(host.encode('idna').decode('ascii'))
            except (UnicodeError, ValueError):
                pass
        decoded = unquote(current)
        if decoded == current:
            break
        current = decoded
    return hosts


def check_url(url: str, include_self: bool = True):
    """차단 대상이면 사용자에게 보여줄 사유 문자열을, 아니면 None 을 반환한다."""
    domains = blocked_domains(include_self)
    tlds = blocked_tlds()

    for host in candidate_hosts(url):
        for domain in domains:
            if host == domain or host.endswith('.' + domain):
                return f'차단된 도메인입니다: {domain}'
        tld = host.rsplit('.', 1)[-1]
        if tld in tlds:
            return f'차단된 최상위 도메인입니다: .{tld}'
    return None


def is_blocked(url: str, include_self: bool = True) -> bool:
    return check_url(url, include_self) is not None

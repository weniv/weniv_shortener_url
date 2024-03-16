from celery import shared_task
from django.db.models import Count
from .models import AccessLog
from datetime import datetime, timedelta
import requests  # Discord에 메시지를 보내기 위해 필요합니다.
from django.conf import settings

DISCORD_WEBHOOK_URL = settings.DISCORD_MAU_WEB_HOOK


@shared_task
def calculate_and_send_statistics():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    last_30_days = today - timedelta(days=30)

    # 어제의 유니크 접속자 수
    yesterday_unique_visits = AccessLog.objects.filter(access_date=yesterday).values('ip_address').distinct().count()

    # 지난 30일간의 유니크 접속자 수
    last_30_days_unique_visits = AccessLog.objects.filter(access_date__gte=last_30_days).values(
        'ip_address').distinct().count()

    # Discord Webhook을 통해 메시지 전송
    webhook_url = DISCORD_WEBHOOK_URL
    message = f"어제의 유니크 접속자 수: {yesterday_unique_visits}, 지난 30일간 유니크 접속자 수: {last_30_days_unique_visits}"
    requests.post(webhook_url,
                  json={
                      "content": f"어제 접속자: {yesterday_unique_visits}명 \n 지난 30일간 접속자(MAU): {last_30_days_unique_visits}명"})

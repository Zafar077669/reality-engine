from celery import shared_task
from companies.models import Company
from signals.services.silent_decay_v2 import detect_silent_support_decay_v2

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 3})
def run_silent_support_decay(self):
    for company in Company.objects.all():
        try:
            detect_silent_support_decay_v2(company)
        except Exception as e:
            # Bu joyda keyin audit/log qo‘shamiz
            print(f"Signal error for {company.id}: {e}")

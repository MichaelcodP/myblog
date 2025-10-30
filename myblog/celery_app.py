import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myblog.settings")

app = Celery("myblog")

app.conf.broker_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
app.conf.result_backend = os.getenv("REDIS_URL", "redis://redis:6379/0")

# recommended serializers
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.timezone = "UTC"

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

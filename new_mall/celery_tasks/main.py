from celery import Celery
import os

#weicelery使用django配置文件进行设置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "new_mall.settings.dev")


#参数1:自定义的一个名字
#参数2:celery保存的redis中
celery_app = Celery('new_mall',
                    broker='redis://127.0.0.1:6379/15')

#自动注册celery任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])
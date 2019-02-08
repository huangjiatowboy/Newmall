from django.contrib import admin

# Register your models here.
from contents import models
#注册模型类到后台
admin.site.register(models.ContentCategory)
admin.site.register(models.Content)
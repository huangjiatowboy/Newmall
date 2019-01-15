from django.conf.urls import url

from new_mall.apps.users import views

urlpatterns = [

    # 发送短信验证码
    url(r'usernames/(?P<username>\w{5,20})/count/', views.UserNameCountView.as_view()),
    url(r'users/', views.CreateUserView.as_view()),
]
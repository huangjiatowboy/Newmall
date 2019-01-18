from django.conf.urls import url

from new_mall.apps.oauth import views

urlpatterns = [

    # QQ登录
    url(r'^oauth/qq/authorization/$', views.QQAuthURLView.as_view()),
    url(r'^oauth/qq/user/$', views.QQUserView.as_view()),
]
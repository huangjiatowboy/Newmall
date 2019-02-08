from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from new_mall.apps.users import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [

    # 发送短信验证码
    url(r'usernames/(?P<username>\w{5,20})/count/', views.UserNameCountView.as_view()),
    url(r'users/$', views.CreateUserView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'user/$', views.UserCenter.as_view()),
    url(r'email/$', views.EmailView.as_view()),
    url(r'email/verification$', views.VerifyEmailView.as_view()),

]
router = DefaultRouter()
router.register(r'addresses',views.AddressViewSet,base_name='addresses')
urlpatterns+=router.urls
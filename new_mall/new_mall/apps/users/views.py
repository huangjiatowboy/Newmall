from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User


from users import serializers

# usernames/(?P<username>\w{5,20})/count/
class UserNameCountView(APIView):
    """判断用户名是否重复"""
    print(1)
    def get(self,request,username):
        # 2.数据库查询用户是否存在
        count = User.objects.filter(username=username).count()
        print(2)
        data = {
            'username':username,
            'count':count
        }
        # 返回响应结果
        return Response(data)


#users
class CreateUserView(CreateAPIView):
    '''用户注册接口'''

    serializer_class = serializers.CreateUserSerializer

from django.conf import settings
from django.shortcuts import render

# Create your views here.
from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from rest_framework import mixins
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users.models import User


from users import serializers

# usernames/(?P<username>\w{5,20})/count/
class UserNameCountView(APIView):
    """判断用户名是否重复"""

    def get(self,request,username):
        # 2.数据库查询用户是否存在
        count = User.objects.filter(username=username).count()

        data = {
            'username':username,
            'count':count,
        }
        # 返回响应结果
        return Response(data)


#users
class CreateUserView(CreateAPIView):
    '''用户注册接口'''

    serializer_class = serializers.CreateUserSerializer

#authorizations/
# class AuthorLogin():

# user
class UserCenter(RetrieveAPIView):
    '''用户个人信息接口'''


    # 2.调用序列化器
    serializer_class = serializers. UserDetailSerializer

    # 1.判断用户是否登录
    permission_classes = [IsAuthenticated]

    # 3.返回结果
    def get_object(self):

        return self.request.user


class EmailView(UpdateAPIView):
    '''保存用户邮箱'''

    #判断用户是否登录
    permission_classes = [IsAuthenticated]

    #调用序列化器
    serializer_class = serializers.EmailSerializer

    def get_object(self,*args,**kwargs):
        #返回详情页序列化
        return self.request.user

class VerifyEmailView(APIView):
    '''激活用户邮箱'''
    # 判断用户是否登录
    permission_classes = [IsAuthenticated]

    def get(self,request):



        #获取token
        token = request.query_params.get('token')

        if not token:

            return Response({'message':'缺少token'},status=400)

            #验证token
        serializer = TimedJSONWebSignatureSerializer(
        	settings.SECRET_KEY, expires_in=60*60*24) # 有效期1天
        try:
            data = serializer.loads(token)

        except BadData:
            return Response({'message':'链接信息失效'},status=400)

        #查询要激活用户对象
        email = data.get('email')

        user_id = data.get('user_id')

        try:
            user = User.objects.get(id=user_id,email=email)

        except User.DoesNotExist:

            return Response({'message':'激活用户不存在'},status=400)

        #修改用户邮箱激活状态
        user.email_active = True
        user.save()

        return Response({'message':'OK'})

class AddressViewSet(mixins.CreateModelMixin,mixins.ListModelMixin,GenericViewSet):
    '''用户地址管理'''
    serializer_class = serializers.UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        #获取当前用户的地址
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        #限制地址个数
        #重写create方法
        count = request.user.addresses.count()
        if count >=2: #每个用户不能超过2个地址
            return Response({'message':'地址个数以达上线'},status=400)

        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        #重写list方法
        #用户地址列表返回数据
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        return Response({
            'user_id':request.user.id,
            'default_address_id':request.user.default_address_id,
            'limit':10,
            'addresses':serializer.data
        })

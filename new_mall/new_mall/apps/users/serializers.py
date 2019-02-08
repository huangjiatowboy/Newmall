import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from celery_tasks.email.tasks import send_verify_email
from users.models import User, Address


class CreateUserSerializer(serializers.ModelSerializer):
    '''用户登录序列化'''
    password2 = serializers.CharField(label='确认密码',write_only=True,)
    sms_code = serializers.CharField(label='短信验证码',write_only=True,)
    allow =  serializers.BooleanField(label='同意协议',write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)
    class Meta:
        model = User
        fields = ('id','username','mobile','password2','allow','password','sms_code','token')
        extra_kwargs = {
            'username':{
                'min_length':5,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许5-20个字符的用户名',
                    'max_length':'仅允许5-20个字符的用户名',
                }
            },

            'password':{
                'write_only':True,
                'min_length':8,
                'max_length':20,
                'error_messages':{
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }

        }

    def validate_mobile(self,value):
        '''验证手机号'''

        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机号格式错误')

        return value

    def validated_allow(self,value):
        '''校验用户是否同意协议'''

        if value is None:
            raise serializers.ValidationError('请勾选用户协议')

    def validate(self, attrs):
        '''校验密码,短信验证码'''


        #判断两次密码是否一致
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码两次输入不一致')

        redis_conn = get_redis_connection('sms_codes')

        mobile = attrs['mobile']

        real_sms_code = redis_conn.get('sms_%s'%mobile)
        real_sms_code = real_sms_code.decode('utf-8')


        #校验是否存在
        if real_sms_code is None:
            raise serializers.ValidationError('验证码无效')
        # 判断验证码是否一致
        if real_sms_code != attrs['sms_code']:
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    def create (self,validated_data):

        user = User.objects.create_user(
                username=validated_data.get('username'),
                password=validated_data.get('password'),
                mobile=validated_data.get('mobile') )

        #注册成功自动登录,需要生成jwt并返回给客户端
        #导包:from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 生payload部分的方法
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成jwt的方法

        # user :登录的用户对象
        payload = jwt_payload_handler(user)  # 生成payload, 得到字典
        token = jwt_encode_handler(payload)  # 生成jwt字符串
        user.token = token

        return user

class UserDetailSerializer(serializers.ModelSerializer):
    '''用户详细信息序列化器'''

    class Meta:
        model = User
        fields = ('id','username','mobile','email','email_active')

class EmailSerializer(serializers.ModelSerializer):
    '''邮箱序列化器'''

    class Meta:

        model = User

        fields = ('id','email')

        extra_kwargs = {
            'email':{
                'required':True
            }
        }

    def update(self, instance, validated_data):

        email = validated_data['email']

        instance.email = validated_data['email']

        instance.save()

        #生成并发送激活邮件
        verify_url = instance.generate_verify_email_url()

        send_verify_email.delay(email,verify_url)

        return instance

class  UserAddressSerializer(serializers.ModelSerializer):
    '''
    用户地址序列化器
    '''
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    #新增字段
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')

        return value

    def create(self,validated_data):
        '''保存'''
        validated_data['user'] = self.context['request'].user

        return super().create(validated_data)

    class Meta:
        model = Address

        exclude = ('user','is_deleted','create_time','update_time')

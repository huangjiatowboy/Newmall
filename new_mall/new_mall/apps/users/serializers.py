import re

from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    '''用户登录序列化'''
    password2 = serializers.CharField(label='确认密码',write_only=True,)
    sms_code = serializers.CharField(label='短信验证码',write_only=True,)
    allow =  serializers.BooleanField(label='同意协议',write_only=True)
    print('xuliehua')
    class Meta:
        model = User
        fields = ('id','username','mobile','password2','allow','password','sms_code')
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

        return User.objects.create_user(
            username=validated_data.get('username'),
            password=validated_data.get('password'),
            mobile=validated_data.get('mobile')

        )
#


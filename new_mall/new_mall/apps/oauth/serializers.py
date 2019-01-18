from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OAuthQQUser
from users.models import User


class QQUserSerializer(serializers.Serializer):
    '''
    QQ登录创建用户序列化器
    '''
    openid= serializers.CharField(label='openid',write_only=True)
    password = serializers.CharField(label='密码',max_length=20,min_length=8,write_only=True)
    sms_code = serializers.IntegerField(label='短信验证码',read_only=True)
    mobile = serializers.RegexField(label='手机号',regex=r'^1[3-9]\d{9}$',write_only=True)

    def validate(self,attrs):
        '''校验'''
        print(attrs)
        mobile = attrs['mobile']
        print(333)
        # sms_code = attrs['sms_code']
        password = attrs['password']

        #校验短信验证码
        # 1.获取redis操作对象
        redis_conn = get_redis_connection('sms_codes')
        # 2.使用手机号,获取短信验证码
        redis_sms_code = redis_conn.get('sms_%s' % mobile)
        # 3.校验手机号是否一致
        # if redis_sms_code is None:
        #
        #     raise serializers.ValidationError({'message':'短信验证码无效'})
        #
        # if redis_sms_code.decode() !=sms_code:
        #
        #     raise serializers.ValidationError({'message':'短信验证码错误'})

        #查询用户
        # 1.通过手机号查询用户是否存在(存在)
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 不存在
            # 以手机号作为用户名进行用户创建
            user = User.objects.create_user(
                username=mobile,
                mobile = mobile,
                password=password
            )
        else:
            # 2.存在校验密码是否正确
            if not user.check_password(password):

                raise serializers.ValidationError({'message':'密码错误'})


        attrs['user'] = user

        return attrs

    def create(self, validated_data):
        #获取校验过的用户
        user = validated_data['user']
        openid = validated_data['openid']

        #绑定openid和美多用户:
        OAuthQQUser.objects.create(
            openid = openid,
            user = user
        )

        return user #返回美多用户
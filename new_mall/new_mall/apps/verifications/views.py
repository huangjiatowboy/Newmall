'''
获取验证码:
1.获取前段传入的手机手机号
2.使用序列化检查手机号码的正确性
2.1redis中查看是否重复发送
3.使用celery异步实现短信发送
4.使用函数生成随机数
5.视图中调用云通讯的短信发送,
6.保存手机号和短信验证到redis
7.保存一分钟之后才能再次发送
'''
import random
import logging

from django_redis import get_redis_connection
from rest_framework.response import Response

from rest_framework.views import APIView




class SmsCodeView(APIView):
    '''发送并保存短信保存redis'''
    def get(self,request,mobile):

        # 1.获取操作redis对象
        strict_redis = get_redis_connection('sms_codes')

        #校验是否可以发送短信
        send_flag = strict_redis.get('send_flag_%s' % mobile)

        if send_flag:
            #没过60秒
            return Response({'message':'发送短信过于频繁'},status=400)

        # 生成随机数
        sms_code = '%06d' % random.randint(0,999999)
        #保存日志
        logging.info('sms_code:%s' % sms_code)
        print('sms_code=',sms_code)

        #调用云通讯 5表示5分钟,1表示测试模版
        # CCP().send_template_sms(mobile,[sms_code,5],1)

        #使用celery发送短信
        # send_sms_code.delay(mobile,sms_code)
        #保存数据到redis
        pl = strict_redis.pipeline()

        pl.setex('sms_%s' % mobile,5*60,sms_code) #过期时间5分钟

        pl.setex('sms_flag_%s' % mobile,60,sms_code) #过期时间1分钟

        result = pl.execute()
        # print(result)

        #响应发送短信验证结果
        return Response({"message":"OK"})
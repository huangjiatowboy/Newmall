from rest_framework.views import exception_handler
import logging
from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework.response import Response
from rest_framework import status

#获取在配置文件中定义的logger,用来记录日志
logger = logging.getLogger('django')

def my_exception_handler(exc,context):
    """
    自定义异常处理
    :param exc: 异常
    :param context:抛出异常的上下文
    :return: Response响应对象
    """
    #调用drf框架原生的异常处理方法
    response = exception_handler(exc,context)

    if response is None:
        #处理所有未被捕的drf异常
        view = context['view']

        error = '[%s]%s' %(view,exc)

        logging.error(error)

        response = Response({'message':'服务器内部错误:%s'% error},500)

    return response
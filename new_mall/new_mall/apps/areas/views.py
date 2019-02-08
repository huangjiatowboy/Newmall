from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area
from areas.serializers import SubAreaSerializer,AreaSerialzer


#继承drf扩展累缓存
class AreasViewSet(ReadOnlyModelViewSet,CacheResponseMixin):
    '''地址三级联动'''
    #设置分页为None
    pagination_class = None
    def get_serializer_class(self):
        '''提供序列化器'''
        if self.action == 'list':

            return AreaSerialzer

        else:

            return SubAreaSerializer

    def get_queryset(self):
        '''提供数据集'''
        if self.action == 'list':

            #查询省级
            return Area.objects.filter(parent=None)

        else:
            #查询所有
            return Area.objects.all()
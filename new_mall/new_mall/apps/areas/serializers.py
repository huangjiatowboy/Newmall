from rest_framework import serializers

from areas.models import Area


class AreaSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Area

        fields = ('id','name')

class SubAreaSerializer(serializers.ModelSerializer):
    '''子行政区划信息序列化器'''
    subs = AreaSerialzer(many=True,read_only=True)

    class Meta:
        model = Area

        fields = ('id','name','subs')
from .models import RosRouter, UserManage, VPNInfo
from rest_framework import serializers


class RosRouterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RosRouter
        fields = '__all__'


class UserManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserManage
        fields = '__all__'


class VPNInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VPNInfo
        fields = '__all__'

from .models import RosRouter, UserManage, VPNInfo
from xadmin.models import UserWidget
from rest_framework import serializers
from django.contrib.auth.models import User


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


class UserWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWidget
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from versatileimagefield.serializers import VersatileImageFieldSerializer

from . import models as app_models


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = app_models.Country
        exclude = ['created', 'modified']


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name']


class PermissionAssignSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    permission_ids = serializers.ListField(child=serializers.IntegerField())


class RoleAssignSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    role_ids = serializers.ListField(child=serializers.IntegerField())


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    country = CountrySerializer(read_only=True)

    class Meta:
        model = app_models.User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'roles', 'country')

    @staticmethod
    def get_roles(instance):
        serializer = GroupSerializer(instance.groups.all(), many=True).data
        return serializer


class UserTokenSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    user = UserSerializer()
    access_token = serializers.CharField(required=True)


class RegisterSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    role = serializers.CharField(required=False)
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    avatar = VersatileImageFieldSerializer(required=False, allow_null=True, sizes='all_image_size')
    country = serializers.IntegerField()
    state = serializers.IntegerField()

    class Meta:
        fields = UserSerializer.Meta.fields

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise ValidationError('Password and Confirm password must be the same.')
        if 'country' in attrs:
            attrs['country'] = app_models.Country.objects.get(pk=attrs.pop('country'))
        super().validate(attrs)
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role')
        _ = validated_data.pop('confirm_password')
        user = app_models.User.objects.create_user(**validated_data)
        if role:
            user.groups.add(Group.objects.get(name=role))
        token = Token.objects.create(user=user)

        return user, token


class LoginSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    email = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(required=True)


class FlightSerializer(serializers.ModelSerializer):
    carrier_name = serializers.ReadOnlyField(source='carrier.name')

    class Meta:
        model = app_models.Flight
        exclude = ['modified', 'created']

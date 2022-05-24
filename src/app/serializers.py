
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


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = app_models.Seat
        fields = ['seat_number', 'status']


class FlightClassSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = app_models.FlightClass
        fields = ['class_name', 'fare', 'capacity', 'seats']


class FlightSerializer(serializers.ModelSerializer):
    carrier_name = serializers.ReadOnlyField(source='carrier.name')
    economy_capacity = serializers.IntegerField(write_only=True)
    premium_capacity = serializers.IntegerField(write_only=True)
    business_capacity = serializers.IntegerField(write_only=True)
    economy_fare = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    premium_fare = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    business_fare = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    classes = FlightClassSerializer(many=True, read_only=True)

    class Meta:
        model = app_models.Flight
        exclude = ['modified', 'created']
        read_only_fields = ['flight_number']

    def create(self, validated_data):
        flight_dict = {key: validated_data[key] for key in [
            "departure_time",
            "departure_date",
            "departure_port",
            "destination_port",
            "duration",
            "carrier"
        ]}
        flight = app_models.Flight.objects.create(**flight_dict)

        economy_class = app_models.FlightClass.objects.create(
            flight=flight,
            class_name=app_models.FlightClass.ECONOMY,
            capacity=validated_data.get('economy_capacity'),
            fare=validated_data.get('economy_fare'),
        )

        for _ in range(economy_class.capacity):
            app_models.Seat.objects.create(flight_class=economy_class)

        premium_class = app_models.FlightClass.objects.create(
            flight=flight,
            class_name=app_models.FlightClass.PREMIUM,
            capacity=validated_data.get('premium_capacity'),
            fare=validated_data.get('premium_fare'),
        )
        for _ in range(premium_class.capacity):
            app_models.Seat.objects.create(flight_class=premium_class)

        business_class = app_models.FlightClass.objects.create(
            flight=flight,
            class_name=app_models.FlightClass.BUSINESS,
            capacity=validated_data.get('business_capacity'),
            fare=validated_data.get('business_fare'),
        )
        for _ in range(business_class.capacity):
            app_models.Seat.objects.create(flight_class=business_class)

        return flight


class PasswordResetSerializer(serializers.Serializer):

    token = serializers.CharField(required=False)
    email = serializers.EmailField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise ValidationError('Password and Confirm password must be the same.')
        super().validate(attrs)
        return attrs

    def save(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        token = validated_data.get('token')
        try:
            user = app_models.User.objects.get(email=email)
        except Exception:
            raise ValidationError('Password reset is not successful. Incorrect email.')

        if app_models.PasswordResetToken.objects.filter(user=user, key=token, status='Active').exists():
            user.set_password(password)
            user.save()
            app_models.PasswordResetToken.objects.filter(user=user, key=token).update(status='Inactive')


class PasswordChangeSerializer(serializers.Serializer):

    password = serializers.CharField()
    confirm_password = serializers.CharField()
    old_password = serializers.CharField()

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise ValidationError('Password and Confirm password must be the same.')
        super().validate(attrs)
        return attrs

    def save(self, validated_data):
        password = validated_data.get('password')
        old_password = validated_data.get('old_password')
        request = self.context.get('request')
        user = request.user
        if user.check_password(old_password):
            user.set_password(password)
            user.save()
        else:
            raise ValueError('Old password is incorrect')


class SocialSerializer(serializers.Serializer):
    """
    This serializer accepts and validates an externally generated OAuth2 access token.
    """

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    access_token = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True
    )

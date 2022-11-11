from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from . import models as app_models, utils


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
    # avatar = VersatileImageFieldSerializer(read_only=True, allow_null=True, sizes='all_image_size')

    class Meta:
        model = app_models.User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'roles', 'country']

    @staticmethod
    def get_roles(instance):
        roles = [role.name for role in instance.groups.all()]
        return roles


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
    country = serializers.IntegerField(required=False)
    avatar_file = serializers.FileField(required=False, write_only=True)

    class Meta:
        fields = UserSerializer.Meta.fields

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise ValidationError('Password and Confirm password must be the same.')
        if 'country' in attrs:
            attrs['country'] = app_models.Country.objects.get(pk=attrs.pop('country'))
        if 'avatar_file' in attrs:
            attrs['avatar'] = attrs.pop('avatar_file')
        super().validate(attrs)
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', None)
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
        fields = ['class_name', 'fare', 'capacity', 'seats', 'available_seats']


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = app_models.Airport
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    carrier_name = serializers.ReadOnlyField(source='carrier.name')
    departure_port = AirportSerializer(read_only=True)
    destination_port = AirportSerializer(read_only=True)
    destination_port_id = serializers.IntegerField(write_only=True)
    departure_port_id = serializers.IntegerField(write_only=True)
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
        read_only_fields = ['flight_number', 'departure_port', 'destination_port']

    def create(self, validated_data):
        flight_dict = {key: validated_data[key] for key in [
            "departure_time",
            "departure_date",
            "duration",
            "carrier"
        ]}
        flight_dict['departure_port'] = app_models.Airport.objects.get(id=validated_data.get('departure_port_id'))
        flight_dict['destination_port'] = app_models.Airport.objects.get(id=validated_data.get('destination_port_id'))
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


class PassenegrSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=15)
    last_name = serializers.CharField(max_length=15)
    gender = serializers.ChoiceField(choices=app_models.Ticket.GENDER_CHOICES)
    dob = serializers.DateField()


class PaymentCardSerilaizer(serializers.Serializer):
    card_name = serializers.CharField(max_length=20)
    number = serializers.CharField(max_length=20)
    cvv = serializers.CharField(max_length=3)
    card_pin = serializers.CharField(max_length=6)
    expiry_month = serializers.CharField(max_length=12)
    expiry_year = serializers.CharField(max_length=2)


class FlightBookingSerializer(serializers.Serializer):
    flight_number = serializers.CharField(max_length=15)
    passenger_count = serializers.IntegerField()
    flight_class = serializers.CharField(max_length=10)
    contact_first_name = serializers.CharField(max_length=15)
    contact_last_name = serializers.CharField(max_length=15)
    contact_phone = serializers.CharField(max_length=15)
    contact_email = serializers.CharField(max_length=15)
    passengers = PassenegrSerializer(many=True)
    payment_card = PaymentCardSerilaizer()

    def save(self, validated_data):
        flight_number = validated_data.get('flight_number')
        passenger_count = validated_data.get('passenger_count')
        flight_class = validated_data.get('flight_class')
        contact_first_name = validated_data.get('contact_first_name')
        contact_last_name = validated_data.get('contact_last_name')
        contact_phone = validated_data.get('contact_phone')
        contact_email = validated_data.get('contact_email')
        passengers = validated_data.get('passengers')
        payment_card = validated_data.get('payment_card')

        flight = app_models.Flight.objects.get(flight_number=flight_number)
        flight_class = app_models.FlightClass.objects.get(flight=flight, class_name=flight_class)
        available_seats = app_models.Seat.objects.filter(
            flight_class=flight_class,
            status=app_models.Seat.AVAILABLE
        )
        if available_seats.count() < passenger_count:
            raise ValidationError('Available seats are fewer than the your requested number of tickets.')

        payment_data = {
            "email": contact_email,
            "amount": str(flight_class.fare * passenger_count*100),
            "pin": payment_card.pop('card_pin'),
            "card": dict(payment_card)
        }

        pay_resp = utils.make_payment(payment_data)
        tickets = []
        if pay_resp['data']['status'] == 'success':
            for num in range(passenger_count):
                seat = available_seats[num]
                passenger = passengers[num]
                ticket = app_models.Ticket.objects.create(
                    first_name=passenger.get('first_name'),
                    last_name=passenger.get('last_name'),
                    gender=passenger.get('gender'),
                    email=contact_email,
                    phone=contact_phone,
                    contact_last_name=contact_last_name,
                    contact_first_name=contact_first_name,
                    seat=seat
                )
                tickets.append(ticket)
        else:
            raise ValidationError('Payment failed.')
        return tickets


class TicketSerializer(serializers.ModelSerializer):
    flight_number = serializers.ReadOnlyField(source="seat.flight_class.flight.flight_number")
    carrier = serializers.ReadOnlyField(source="seat.flight_class.flight.carrier.name")
    flying_from = serializers.ReadOnlyField(source="seat.flight_class.flight.departure_port.name")
    flying_to = serializers.ReadOnlyField(source="seat.flight_class.flight.destination_port.name")
    date = serializers.ReadOnlyField(source="seat.flight_class.flight.departure_date")
    time = serializers.ReadOnlyField(source="seat.flight_class.flight.departure_time")

    class Meta:
        model = app_models.Ticket
        fields = '__all__'


class CarrierSerializer(serializers.ModelSerializer):

    class Meta:
        model = app_models.Carrier
        fields = '__all__'

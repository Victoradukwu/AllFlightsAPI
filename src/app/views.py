
import math
import uuid

import django_filters
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from requests import HTTPError
from rest_framework import filters, generics
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from social_django.utils import psa

from .models import User, Country, Flight, PasswordResetToken, Ticket
from . import serializers, docs, utils


class PageSizeAndNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        page_resp = super().get_paginated_response(data)
        page_obj = page_resp.data
        num_of_pages = math.ceil(page_obj['count']/self.page_size)
        page_obj['number_of_pages'] = num_of_pages
        return Response(page_obj)


@swagger_auto_schema(method='post', request_body=serializers.RegisterSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = serializers.RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user, token = serializer.save()

    data = {"user": user, "access_token": token.key}
    return Response(serializers.UserTokenSerializer(data).data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method='post', request_body=serializers.LoginSerializer)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    wrong_credentials = {"detail": "Wrong credentials."}
    serializer = serializers.LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    if data.get('email'):
        user = authenticate(request, email=data['email'], password=data['password'])
    elif data.get('phone_number'):
        user = authenticate(request, phone_number=data['phone_number'], password=data['password'])
    else:
        return Response({'detail': 'Please provide email or phone number.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user:
        return Response(wrong_credentials, status=status.HTTP_401_UNAUTHORIZED)

    token, created = Token.objects.get_or_create(user=user)

    data = {"user": user, "access_token": token.key}

    return Response(serializers.UserTokenSerializer(data).data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view()
@permission_classes([AllowAny])
def logout(request):
    Token.objects.filter(user=request.user).delete()

    return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)


@api_view()
@permission_classes([AllowAny])
def initiate_password_reset(request, email):
    user = User.objects.filter(email=email).first()
    if user:
        token = uuid.uuid4().hex
        PasswordResetToken.objects.create(user=user, key=token, status='Active')

        email_body = f'<html>' \
                     f'<head>' \
                     f'</head>' \
                     f'<body>' \
                     f'<p>Hi {user.first_name},</p>' \
                     f'<p>You requested for a password reset on <b>Allflights</b></p>' \
                     f'<p>Kindly click on the link below to reset your password</p>' \
                     f'<a href="https:www.allflights.com/auth/password-reset/{token}">Reset password</a>' \
                     f'</body>' \
                     f'</html>'

        payload = {
            'subject': 'Password Reset',
            'html_content': email_body,
            'to_email': user.email
        }
        utils.send_email(payload)
    return Response({'detail': 'Check your email'})


@swagger_auto_schema(method='post', request_body=serializers.PasswordResetSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def complete_password_reset(request):
    serializer = serializers.PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    serializer.save(serializer.validated_data)
    return Response({'detail': 'Password reset successful'})


@swagger_auto_schema(method='post', request_body=serializers.PasswordChangeSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = serializers.PasswordChangeSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    try:
        serializer.save(serializer.validated_data)
    except ValueError as exc:
        return Response({'detail': str(exc)})
    return Response({'detail': 'Password change successful'})


class RoleListView(ListCreateAPIView):
    """
       get:
       Return a list of role objects

       post:
       creates a new role object
    """
    serializer_class = serializers.GroupSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PageSizeAndNumberPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = '__all__'

    def get_queryset(self):
        return Group.objects.all()


class RoleDetailView(RetrieveUpdateDestroyAPIView):
    """
    get:
    Return the details of a single role

    put:
    Updates a given role, non-partial update

    patch:
    Updates a given role, partial update

    delete:
    Deletes a single role
    """

    permission_classes = [IsAdminUser]
    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        return Group.objects.all()

    def get_object(self):
        id_ = self.kwargs.get('pk')
        group = Group.objects.get(id=id_)
        return group


class PermissionListView(ListCreateAPIView):
    """
       get:
       Return a list of permission objects

       post:
       creates a new permission object
    """

    serializer_class = serializers.PermissionSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PageSizeAndNumberPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code_name']
    ordering_fields = '__all__'

    def get_queryset(self):
        return Permission.objects.all()


class PermissionDetailView(RetrieveUpdateDestroyAPIView):
    """
        get:
        Return the details of a permission flight

        put:
        Updates a given permission, non-partial update

        patch:
        Updates a given permission, partial update


        delete:
        Deletes a single permission
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.PermissionSerializer

    def get_queryset(self):
        return Permission.objects.all()

    def get_object(self):
        id_ = self.kwargs.get('pk')
        permission = Permission.objects.get(id=id_)
        return permission


class CountryListView(ListAPIView):
    """
       get:
       Return a list of country objects

    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.CountrySerializer

    def get_queryset(self):
        return Country.objects.all()


@swagger_auto_schema(**docs.user_permission)
@api_view(http_method_names=['POST'])
@permission_classes([AllowAny])
def assign_permissions(request, principal, operation, id_):
    """

    Parameters
    ----------
    id_ : str
        the primary key of the user or role to assign permission
    principal : str
        the type of entity to assign or remove permissions ['user' or 'group']
    operation : str
        the type of operation to carry out on the permissions ['add' or 'remove']

    """
    serializer = serializers.PermissionAssignSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ids = serializer.validated_data.get('permission_ids')

    if operation == 'add':
        if principal == 'user':
            user = User.objects.get(pk=id_)
            user.user_permissions.add(*ids)
        else:
            role = Group.objects.get(pk=id_)
            role.permissions.add(*ids)

    else:
        if principal == 'user':
            user = User.objects.get(pk=id_)
            user.user_permissions.remove(*ids)
        else:
            role = Group.objects.get(pk=id_)
            role.permissions.remove(*ids)
    return Response({'detail': 'Successful'})


@swagger_auto_schema(method='post', request_body=serializers.RoleAssignSerializer)
@api_view(http_method_names=['POST'])
@permission_classes([IsAdminUser])
def assign_roles_to_user(request, pk, operation):

    user = User.objects.get(pk=pk)
    serializer = serializers.RoleAssignSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ids = serializer.validated_data.get('role_ids')
    if operation == 'add':
        user.groups.add(*ids)
    else:
        user.groups.remove(*ids)
    return Response({'detail': 'Successful'})


@api_view(http_method_names=['GET'])
@permission_classes([AllowAny])
def recommendations(request, departure_port, departure_date):
    # recommendations_host = os.getenv('RECOMMENDATIONS_HOST', 'localhost')
    # url = f'http://{recommendations_host}:8100/{departure_port}/{departure_date}'
    # resp = requests.get(url)
    # if resp.ok:
    #     data = resp.json()
    #     for flt in data:
    #         flt['carrier_name'] = Flight.objects.get(id=flt.get('id')).carrier.name
    # else:
    #     print(resp.json())
    #     data = 'There is an error'
    # return Response({'detail': data})
    flights = Flight.objects.filter(departure_port=departure_port, departure_date=departure_date)
    return Response(serializers.FlightSerializer(flights, many=True).data)


class FlightListView(ListCreateAPIView):
    """
       get:
       Return a list of flight objects

       post:
       creates a new flight object
   """

    permission_classes = [utils.IsAdminOrReadOnly]
    serializer_class = serializers.FlightSerializer
    filterset_class = utils.FlightFilter
    pagination_class = PageSizeAndNumberPagination

    def get_queryset(self):
        return Flight.objects.all()


class FlightDetailView(RetrieveUpdateDestroyAPIView):
    """
    get:
    Return the details of a single flight

    put:
    Updates a given flight, non-partial update

    patch:
    Updates a given flight, partial update

    delete:
    Deletes a single flight
    """

    permission_classes = [IsAdminUser]
    serializer_class = serializers.FlightSerializer

    def get_queryset(self):
        return Flight.objects.all()

    def get_object(self):
        id_ = self.kwargs.get('pk')
        flight = Flight.objects.get(id=id_)
        return flight


@swagger_auto_schema(method='post', request_body=serializers.SocialSerializer)
@api_view(http_method_names=['POST'])
@parser_classes([FormParser])
@psa()
def exchange_token(request, backend):
    """

       Parameters
       ----------
       request : DRF request
            Instance of DRF request object
       backend : str
           the social authentication backend in use. Choices are: [facebook, google-oauth2]

       """
    serializer = serializers.SocialSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        try:
            user = request.backend.do_auth(serializer.validated_data['access_token'])
        except HTTPError as e:
            return Response(
                {'errors': {
                    'token': 'Invalid token',
                    'detail': str(e),
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user:
            return Response(
                {'errors': {'non_field_errors': "Authentication Failed"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_active:
            token, _ = Token.objects.get_or_create(user=user)
            payload = {
                'message': "Successfully logged in",
                'token': token.key,
                'data': serializers.UserSerializer(user).data
            }
            payload['data']['isStaff'] = user.is_staff
            return Response(payload, status=status.HTTP_200_OK)
        else:
            return Response(
                {'errors': {'non_field_errors': 'This user account is inactive'}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TicketListView(generics.ListCreateAPIView):
    """A class view for creating and listing all tickets"""

    permission_classes = [utils.IsAdminOrCreateOnly]
    # filterset_class = TicketFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.TicketSerializer
        return serializers.FlightBookingSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(email=self.request.user.email).order_by('id')

    def get(self, request):
        tickets = self.get_queryset()
        return Response({'detail': serializers.TicketSerializer(tickets, many=True).data})

    def post(self, request):
        """
            Book flight ticket. Use the following test card details

            "pin": "1111",
            "number": "507850785078507812",
            "cvv": "081",
            "expiry_month": "05",
            "expiry_year":  "23"
            """
        data = request.data
        serializer = serializers.FlightBookingSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        tickets = serializer.save(serializer.validated_data)
        return Response(
            {
                'message': 'Ticket(s) successfully booked.',
                'detail': serializers.TicketSerializer(tickets, many=True).data
            },
            status=status.HTTP_200_OK)

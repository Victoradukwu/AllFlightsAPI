
from django.urls import path

from . import views
urlpatterns = [
    path('auth/roles/', views.RoleListView.as_view(), name='role_list'),
    path('auth/roles/<pk>/', views.RoleDetailView.as_view(), name='role_details'),
    path('auth/permissions/', views.PermissionListView.as_view(), name='perms_list'),
    path('auth/permissions/<pk>/', views.PermissionDetailView.as_view(), name='perms_details'),
    path('auth/permissions/<principal>/<id>/<operation>/', views.assign_permissions, name='assign_perms'),
    path('auth/users/<pk>/roles/<operation>/', views.assign_roles_to_user, name='assign_user_roles'),
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/initiate-password-reset/<email>/', views.initiate_password_reset, name='reset_init'),
    path('auth/complete-password-reset/', views.complete_password_reset, name='reset_complete'),
    path('auth/change-password/', views.change_password, name='change_complete'),
    path('auth/social/<backend>/', views.exchange_token, name='social_auth'),
    path('countries/', views.CountryListView.as_view(), name='countries'),
    path('flights/', views.FlightListView.as_view(), name='flight_list'),
    path('flights/<pk>/', views.FlightDetailView.as_view(), name='flight_detail'),
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('tickets/<pk>/', views.FlightDetailView.as_view(), name='ticket_detail'),
    path('flights/recommendations/<departure_port>/<departure_date>', views.recommendations, name='recommendations'),
    path('carriers/', views.CarrierListView.as_view(), name='carriers'),
    path('airports/', views.AirportListView.as_view(), name='airports'),
]

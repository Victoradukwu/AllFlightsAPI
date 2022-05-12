
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
    path('auth/initiate-password-reset/<email>/', views.initiate_password_reset, name='reset_init'),
    path('auth/complete-password-reset/', views.complete_password_reset, name='reset_complete'),
    path('auth/change-password/', views.change_password, name='change_complete'),
    path('countries/', views.CountryListView.as_view(), name='countries'),
    path('flights/', views.FlightListView.as_view(), name='flights'),
    path('flights/recommendations/<departure_port>/<departure_date>', views.recommendations, name='recommendations')
]

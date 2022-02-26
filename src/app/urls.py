
from django.urls import path

from . import views
urlpatterns = [
    path('auth/roles/', views.RoleListView.as_view(), name='role_list'),
    path('auth/roles/<pk>/', views.RoleDetailView.as_view(), name='role_details'),
    path('auth/permissions/', views.PermissionListView.as_view(), name='perms_list'),
    path('auth/permissions/<pk>/', views.PermissionDetailView.as_view(), name='perms_details'),
    path('auth/users/<pk>/permissions/', views.assign_permissions_to_user, name='assign_user_perms'),
    path('auth/users/<pk>/roles/', views.assign_roles_to_user, name='assign_user_roles'),
    path('auth/groups/<pk>/permissions/', views.assign_permissions_to_group, name='assign_group_perms'),
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('countries/', views.CountryListView.as_view(), name='countries'),
    path('flights/', views.FlightListView.as_view(), name='flights')
]


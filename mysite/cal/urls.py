from django.urls import path, include
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path('', views.month_view, name='month_view'),
    path('no_auth/', views.no_auth, name='no_auth'),
    path('no_perm/', views.no_perm, name='no_perm'),
    path('no_exists/', views.no_exists, name='no_exists'),
    path('success/', views.success, name='success'),
    path('switch_location/', views.switch_location, name='switch_location'),
    path('<int:year>/<int:month>', views.month_view, name='month_req'),
    path('view_subrequest/<int:sub_id>', views.view_subrequest, name='view_subrequest'),
    path('delete_subrequest/<int:req_id>', views.delete_subrequest, name='delete_subrequest'),
    path('toggle_declare_sub/<int:sub_id>', views.toggle_declare_sub, name='toggle_declare_sub'),
    path('toggle_approve_subrequest/<int:sub_id>', views.toggle_approve_subrequest, name='toggle_approve_subrequest'),
    path('view_shift/<int:shift_id>', views.view_shift, name='view_shift'),
    path('delete_shift/<int:shift_id>', views.delete_shift, name='view_shift'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('create_shift', views.create_shift, name='create_shift'),
    path('create_subrequest', views.create_subrequest, name='create_subrequest'),
    path('create_shifts', views.create_shifts, name='create_shifts'),
    path('change_password', auth_views.PasswordChangeView.as_view(template_name='cal/change_password.html', success_url='success'), name='change_password'),
    path('calculate_hours', views.calculate_hours, name='calculate_hours'),    
]

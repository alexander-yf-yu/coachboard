from django.urls import path, include
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path('index', views.index, name='cal_index'),
    path('', views.month_view, name='month_view'),
    path('<int:year>/<int:month>', views.month_view, name='month_req'),
    path('view_subrequest/<int:sub_id>', views.view_subrequest, name='view_subrequest'),
    path('delete_subrequest/<int:req_id>', views.delete_subrequest, name='delete_subrequest'),
    path('declare_sub/<int:sub_id>', views.declare_sub, name='declare_sub'),
    path('revoke_sub/<int:sub_id>', views.revoke_sub, name='revoke_sub'),
    path('approve_subrequest/<int:sub_id>', views.approve_subrequest, name='approve_subrequest'),
    path('view_shift/<int:shift_id>', views.view_shift, name='view_shift'),
    path('delete_shift/<int:shift_id>', views.delete_shift, name='view_shift'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('success', views.success, name='success'),
    path('no_auth', views.no_auth, name='no_auth'),
    path('no_perm', views.no_perm, name='no_perm'),
    path('no_exists', views.no_exists, name='no_exists'),
    path('create_shift', views.create_shift, name='create_shift'),
    path('create_subrequest', views.create_subrequest, name='create_subrequest'),
    path('create_shiftgroup', views.create_shiftgroup, name='create_shiftgroup'),
    path('change_password', auth_views.PasswordChangeView.as_view(template_name='cal/change_password.html', success_url='success'), name='change_password'),
    path('calculate_hours', views.calculate_hours, name='calculate_hours'),
    
]

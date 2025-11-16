from django.urls import path
from django.contrib.auth import views as auth_views
from . import views



class LogoutViewPOST(auth_views.LogoutView):
    template_name = 'oauth2_service/logged_out.html'
    http_method_names = ['post']

urlpatterns = [
    path('', views.home, name='home'),
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/update/<int:pk>/', views.client_update, name='client_update'),
    path('clients/delete/<int:pk>/', views.client_delete, name='client_delete'),
    path('login/', auth_views.LoginView.as_view(template_name='oauth2_service/login.html'), name='login'),
    path('logout/', LogoutViewPOST.as_view(next_page='home'), name='logout'),

    # Custom Auth endpoints
    path('custom-auth2/', views.custom_auth_login, name='custom_auth_login'),
    path('oauth2/callback', views.custom_auth_callback, name='custom_auth_callback'),

    # OAuth2 endpoints
    path('oauth2/authorize', views.oauth2_authorize, name='oauth2_authorize'),
    path('oauth2/token', views.oauth2_token, name='oauth2_token'),
    path('userinfo', views.userinfo, name='userinfo'),
]

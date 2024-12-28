from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('agradecimento/', views.agradecimento, name='agradecimento'),  # Corrigido o nome da URL
    path('dashboard/', views.dashboard, name='dashboard'),  # Definição única para o dashboard
    path('status_leads/<int:pk>/', views.status_envelope_leads, name='status-leads'),
    path('accounts/login/', views.custom_login, name='login'),  # URL para login
    path('accounts/login/redirect/', views.login_redirect, name='login_redirect'),  # URL para redirecionamento após login
    path('accounts/login/<str:user>/dashboard/', views.dashboard, name='user_dashboard'),  # Nome alterado para evitar conflito
    path('webhook/', views.webhook, name='webhook'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
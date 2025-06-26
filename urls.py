
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),                    
    path('chatbot/', views.chatbot, name='chatbot'),      
    path('scan/', views.scan, name='scan'),  
    path('logout/', views.logout_view, name='logout'),
    path('sifre-sifirla/', views.forgot_password, name='forgot_password'),
    path('sifre-sifirla/gonderildi/', auth_views.PasswordResetDoneView.as_view(template_name='chat/password_reset_done.html'), name='password_reset_done'),
    path('sifre-sifirla/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='chat/password_reset_confirm.html'), name='password_reset_confirm'),
    path('sifre-sifirla/tamamlandi/', auth_views.PasswordResetCompleteView.as_view(template_name='chat/password_reset_complete.html'), name='password_reset_complete'),
    path('sifre-sifirla/', auth_views.PasswordResetView.as_view(template_name='chat/password_reset.html'), name='password_reset'),

]

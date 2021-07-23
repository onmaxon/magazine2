from django.urls import path
import authapp.views as authapp

app_name = 'authapp'

urlpatterns = [
    path('login/', authapp.login, name='login'),
    path('logout/', authapp.MyLogoutView.as_view(), name='logout'),
    path('register/', authapp.UserRegisterView.as_view(), name='register'),
    path('edit/', authapp.UserUpdateView.as_view(), name='edit'),
    path('verify/<email>/<key>/', authapp.verify, name='verify')
]

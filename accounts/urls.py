from django.contrib import admin
from django.urls import path
from .import views
app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("new_vaccess_token/", views.RefreshTokenView.as_view(), name="refresh_token"),
    path("verify_company_details_before_registering/", views.CustomerCompanyVerificationView.as_view(), name="verify_company_details_before_registering"),
    path("verify_user_details_before_registering/", views.UserDetailsVerificationView.as_view(), name="verify_user_details_before_registering"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]

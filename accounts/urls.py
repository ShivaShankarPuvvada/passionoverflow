from django.urls import path, re_path
from .import views
from django.contrib.auth import views as auth_views

app_name = "accounts"

"""
We used custom JWT creation decoding encoding generating access_token and refresh_tokens
Frontend will handle those tokens
There are mainly two types of users. Contributors (has all the access) if added to the project, Collaborator has only tickets and posts wide access.
company sub domain name will be suggested. this is optional, they can choose any kind of sub domain name if available
username will be suggested. this is optional, they can choose any kind of username if available
first user will create the profile in our account in a company. He will have to invite the remaining people by allowing them to spaces/company sub domains. He can make invited users as root users as well.
If company is already there, we need to ask the user to contact his adminstrator.
Payment should be taken care of for a single company. i.e, for a single company, single payment account is sufficient. Any root user/contributor in the company can pay.
"""

urlpatterns = [
    re_path(r"login/$", auth_views.LoginView.as_view(template_name="accounts/login.html"),name='login'),
    re_path(r"logout/$", auth_views.LogoutView.as_view(), name="logout"),
    
    # path("login/", views.LoginView.as_view(), name="login"),
    # path("logout/", views.LogoutView.as_view(), name="logout"),
    # path("registration/", views.RegistrationView.as_view(), name="registration"),
    # path("verify_company_details_before_registering/", views.CustomerCompanyVerificationView.as_view(), name="verify_company_details_before_registering"), # it will verify the company name or sub domain name already exists or not.
    # path("verify_user_details_before_registering/", views.UserDetailsVerificationView.as_view(), name="verify_user_details_before_registering"), # this will verify email or phone or username exists or not.
    # path("profile/", views.ProfileView.as_view(), name="profile"),
    # path("give_contributor_access_to_collaborators/", views.GiveContributorAccessToCollaborators.as_view(), name="give_contributor_access_to_collaborators"),
    # path("remove_contributor_access/", views.GiveContributorAccessToCollaborators.as_view(), name="remove_contributor_access"),
    # path("suggest_username/", views.SuggestUsernameView.as_view(), name="suggest_username"), # this will suggest a new username which is not existed in the database.
    # path("company_sub_domain_name/", views.SuggestCompanySubDomainNameView.as_view(), name="company_sub_domain_name") # this will suggest a new company sub domain name which is not already existed in the database.
]

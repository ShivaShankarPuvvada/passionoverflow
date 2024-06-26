from django.urls import reverse

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login

from django.contrib.auth.views import LoginView, LogoutView

from django.db import transaction, IntegrityError
from django.db.models import Q

from django_countries import countries

from .models import GENDER_IN_CHOICES, CustomerCompanyDetails, Company

from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

from http import HTTPStatus
import re

User = get_user_model()

# Create your views here.
@csrf_exempt
def check_availability(request):
    field = request.GET.get('field')
    value = request.GET.get('value')
    response = {'exists': False}

    if field and value:
        if field == 'username' and User.objects.filter(username=value).exists():
            response['exists'] = True
        elif field == 'company_sub_domain_name' and Company.objects.filter(sub_domain_name=value).exists():
            response['exists'] = True
        elif field == 'email' and User.objects.filter(email=value).exists():
            response['exists'] = True
        elif field == 'phone_number' and User.objects.filter(phone_number=value).exists():
            response['exists'] = True

    return JsonResponse(response)


def registration_view(request):

    """
    username, email, phone_number and company_sub_domain_name are unique fields. 
    We don't need to validate if they already exists in our db or not. 
    Even though they submit the form, they will get unexpected error.
    Also, it will show error below the html fields that these are already taken.
    """
    if request.method == "POST":
        try:
            data = request.POST
            must_keys = ["full_name", "username", "email", "password", "company_name", "phone_number", "company_sub_domain_name"]

            if bool(set(must_keys) - set(data.keys())):
                return JsonResponse({'success': False, 'Message': str(set(must_keys) - set(data.keys())) + " missing"}, status=HTTPStatus.BAD_REQUEST)

            # Extract user data
            full_name = data["full_name"]
            username = data["username"]
            email = data["email"]
            password = data["password"]
            company_name = data["company_name"]
            phone_number = data["phone_number"]
            company_sub_domain_name = data["company_sub_domain_name"]

            # Basic validation
            errors = []
            
            if not full_name:
                errors.append("Full name is required.")
            if not username:
                errors.append("Username is required.")
            if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                errors.append("Enter a valid email address.")
            if not password or not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$", password):
                errors.append("Password does not match these rules: min 8 letters, should contain at least one number, one uppercase, one lowercase, one symbol.")
            if not company_name:
                errors.append("Company name is required.")
            if not phone_number or not re.match(r"^\+?\d{10,15}$", phone_number):  # Basic phone number validation
                errors.append("Enter a valid phone number.")
            if not company_sub_domain_name:
                errors.append("Company space name is required.")
            
            if errors:
                return JsonResponse({'success': False, 'errors': errors})

            with transaction.atomic():

                # Create user
                user = User.objects.create(
                    full_name=full_name,
                    username=username,
                    email=email
                )
                user.set_password(password)
                user.save()

                # Create company
                company, company_created = Company.objects.get_or_create(name=company_name, sub_domain_name=company_sub_domain_name)
                if company_created:
                    company.created_by = user
                company.save(user=request.user)

                # Create customer company details
                company_customer, company_customer_created = CustomerCompanyDetails.objects.get_or_create(company=company, company_root_user=user)
                if company_customer_created:
                    company_customer.created_by = user
                company_customer.save(user=request.user)

            return JsonResponse({'success': True, 'redirect_url': reverse('accounts:login')})

        except Exception as error:
            print(error)
            # Rollback the transaction and return an error response
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again.",]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    elif request.method == "GET":
        try:
            return render(request, "accounts/signup.html")
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return JsonResponse({'Message': error_message }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': reverse('projects:project_list')})  # Replace with your success URL
        else:
            return JsonResponse({'success': False, 'error': 'Invalid username or password'}, status=HTTPStatus.BAD_REQUEST)
    
    return render(request, 'accounts/login.html')


# class ProfileView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def get(self, request):
#         try:
#             # Retrieve country data from django-countries
#             country_data = [{'code': code, 'name': name} for code, name in list(countries)]
#             response_data = {
#                 'countries': country_data,
#                 'genders': GENDER_IN_CHOICES,
#             }
#             return JsonResponse(response_data, status=HTTPStatus.HTTP_200_OK)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return JsonResponse({'Message': error_message }, status=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         try:
#             data=request.data
#             must_keys=[]
#             if bool(set(must_keys)-set(data.keys())):
#                 return JsonResponse({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=HTTPStatus.HTTP_400_BAD_REQUEST)

#             serializer = UserCreationSerializer(data)
#             if serializer.is_valid():
#                 serializer.save(user=request.user)
#                 profile_url = reverse("accounts:profile")  # Replace "login" with the name of your login view
#                 response_data = {
#                     'data': serializer.data,
#                     "message": "Data Saved Successfully.",
#                     "profile_url": profile_url,
#                 }
#                 return JsonResponse(response_data, status=HTTPStatus.HTTP_200_OK)
#             else:
#                 response_data = {
#                     'data': {},
#                     "message": "No New Data Passed.",
#                     "profile_url": profile_url,
#                 }
#                 return JsonResponse(response_data, status=HTTPStatus.HTTP_200_OK)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return JsonResponse({'Message': error_message }, status=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR)


# class GiveContributorAccessToCollaborators(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         try:
#             data = request.data
#             must_keys = ["user_ids", "company_id"]

#             # Check if required keys are present
#             if bool(set(must_keys) - set(data.keys())):
#                 return JsonResponse({'Message': str(set(must_keys) - set(data.keys())) + " missing"}, status=HTTPStatus.HTTP_400_BAD_REQUEST)

#             # Get contributor's email and company_id from request data
#             user_ids = data.get('user_ids')
#             company_id = data.get('company_id')

#             # Retrieve the logged-in user making the request
#             user = request.user

#             # Check if the logged-in user is the root user of the specified company
#             logged_in_user_company = get_object_or_404(CustomerCompanyDetails, company__id=company_id, company_root_user=user)

#             with transaction.atomic():
#                 for collaborator_id in user_ids:
#                     collaborator = get_object_or_404(User, id=collaborator_id)

#                     # Check if the adding user is the user of the specified company.
#                     customer_company_details = CustomerCompanyDetails.objects.filter(company__id=company_id, company_user=collaborator)

#                     if customer_company_details.exits(): # ignoring the fact that user will exist and companydetails will not exist.

#                         # Assign contributor access to the collaborator
#                         customer_company_details.company_root_user = collaborator
#                         customer_company_details.save(user=request.user)

#                 response_data = {
#                     'message': f'Contributor access granted for given user ids.',
#                     'user_ids': user_ids,
#                     'company_id': company_id,
#                 }

#             return JsonResponse(response_data, status=HTTPStatus.HTTP_200_OK)

#         except IntegrityError as integrity_error: # this error relates to database.
#             error_message = "Integrity Error: " + str(integrity_error)
#             return JsonResponse({'Message': error_message}, status=HTTPStatus.HTTP_400_BAD_REQUEST)

#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error)
#             return JsonResponse({'Message': error_message}, status=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR)


# class RemoveContributorAccess(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         try:
#             data = request.data
#             must_keys = ["user_ids", "company_id"]

#             # Check if required keys are present
#             if bool(set(must_keys) - set(data.keys())):
#                 return JsonResponse({'Message': str(set(must_keys) - set(data.keys())) + " missing"}, status=HTTPStatus.HTTP_400_BAD_REQUEST)

#             # Get contributor's email and company_id from request data
#             user_ids = data.get('user_ids')
#             company_id = data.get('company_id')

#             # Retrieve the logged-in user making the request
#             user = request.user

#             # Check if the logged-in user is the root user of the specified company
#             logged_in_user_company = get_object_or_404(CustomerCompanyDetails, company__id=company_id, company_root_user=user)

#             with transaction.atomic():
#                 for contributor_id in user_ids:
#                     contributor = get_object_or_404(User, id=contributor_id)

#                     # Check if the removing root access user is the user of the specified company also.
#                     customer_company_details = CustomerCompanyDetails.objects.filter(company__id=company_id, company_root_user=contributor)
#                     if customer_company_details.exits():
#                         # Assign contributor access to the collaborator
#                         customer_company_details.company_root_user = None
#                         customer_company_details.save(user=request.user)



#                 response_data = {
#                     'message': f'Contributor access removed for given user ids.',
#                     'user_ids': user_ids,
#                     'company_id': company_id,
#                 }

#             return JsonResponse(response_data, status=HTTPStatus.HTTP_200_OK)

#         except IntegrityError as integrity_error: # this error relates to database.
#             error_message = "Integrity Error: " + str(integrity_error)
#             return JsonResponse({'Message': error_message}, status=HTTPStatus.HTTP_400_BAD_REQUEST)

#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error)
#             return JsonResponse({'Message': error_message}, status=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR)

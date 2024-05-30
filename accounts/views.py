from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse

from django.contrib.auth import get_user_model

from django_countries import countries
from .models import GENDER_IN_CHOICES, CustomerCompanyDetails, Company
from django.db.models import Q

from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
from http import HTTPStatus
import re
from django.db import transaction

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
    get method is not needed. we don't need to send anything to frontend.
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
                company.save()

                # Create customer company details
                company_customer, company_customer_created = CustomerCompanyDetails.objects.get_or_create(company=company, company_root_user=user)
                if company_customer_created:
                    company_customer.created_by = user
                company_customer.save()

            return JsonResponse({'success': True, 'redirect_url': reverse('accounts:login')})

        except Exception as error:
            # Rollback the transaction and return an error response
            return JsonResponse({'success': False, 'errors': ["An unexpected error occurred. Please try again.",]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    elif request.method == "GET":
        try:
            return render(request, "accounts/signup.html")
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return JsonResponse({'Message': error_message }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


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
#                 serializer.save()
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


# class LoginView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def get(self, request):
#         try:
#             return JsonResponse({}, status=HTTPStatus.HTTP_200_OK)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return JsonResponse({'Message': error_message }, status=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         try:
#             data=request.data
#             must_keys=["username", "password"]
#             if bool(set(must_keys)-set(data.keys())):
#                 return JsonResponse({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=HTTPStatus.HTTP_400_BAD_REQUEST)

#             obtain_token_instance = ObtainTokenView()
#             response_from_obtain_token = obtain_token_instance.post(request)
#             token_response_dictionary = response_from_obtain_token.data
#             access_token = token_response_dictionary['access_token']
#             refresh_token = token_response_dictionary['refresh_token']
#             user = token_response_dictionary['user']
#             user_serializer = UserJsonResponseSerializer(user)
#             return JsonResponse({'access_token': access_token, 'refresh_token': refresh_token, 'user': user_serializer.data}, status=HTTPStatus.HTTP_200_OK)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return JsonResponse({'Message': error_message }, status=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR)


# class LogoutView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request):
#         try:
#             # return JsonResponse({"error": e}, status=HTTPStatus.HTTP_400_BAD_REQUEST)
#             tokens = request.data.get("tokens")
#             if "refresh_token" in tokens:
#                 del tokens["refresh_token"]
#             return JsonResponse({"message": "Logout successful."}, status=HTTPStatus.HTTP_204_NO_CONTENT)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return JsonResponse({'Message': error_message }, status=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR)




# def suggest_username(full_name):
#     # Extract initials from full name
#     initials = ''.join([name[0] for name in full_name.split()])

#     # Generate a username using initials
#     suggested_username = initials.lower()

#     # Check if the username already exists
#     suffix = 1
#     while User.objects.filter(username=suggested_username).exists():
#         suggested_username = f"{initials.lower()}{suffix}"
#         suffix += 1

#     return suggested_username


# class SuggestUsernameView(APIView):
#     def post(self, request):

#         try:
#             data=request.data
#             # Check if must_keys are present
#             must_keys=["full_name", ]
#             if bool(set(must_keys)-set(data.keys())):
#                 return JsonResponse({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=HTTPStatus.HTTP_400_BAD_REQUEST)

#             # Check if full_name is empty
#             if not data['full_name']:
#                 return JsonResponse({'Message': 'Full name cannot be empty.'}, status=HTTPStatus.HTTP_400_BAD_REQUEST)

#             full_name = request.data.get('full_name')
#             suggested_username = suggest_username(full_name)
#             return JsonResponse({'suggested_username': suggested_username}, status=HTTPStatus.HTTP_200_OK)

#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return JsonResponse({'Message': error_message }, status=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR)




# def suggest_company_sub_domain_name(company_name):
#     # Extract initials from company name
#     initials = ''.join([name[0] for name in company_name.split()])

#     # Generate a sub domain using initials
#     suggested_sub_domain_name = initials.lower()

#     # Check if the username already exists
#     suffix = 1
#     while Company.objects.filter(sub_domain_name=suggested_sub_domain_name).exists():
#         suggested_sub_domain_name = f"{initials.lower()}{suffix}"
#         suffix += 1

#     return suggested_sub_domain_name



# class SuggestCompanySubDomainNameView(APIView):
#     def post(self, request):

#         try:
#             data=request.data
#             # Check if must_keys are present
#             must_keys=["company_name", ]
#             if bool(set(must_keys)-set(data.keys())):
#                 return JsonResponse({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=HTTPStatus.HTTP_400_BAD_REQUEST)

#             # Check if company_name is empty
#             if not data['company_name']:
#                 return JsonResponse({'Message': 'Company name cannot be empty.'}, status=HTTPStatus.HTTP_400_BAD_REQUEST)

#             company_name = request.data.get('company_name')
#             suggested_company_sub_domain_name = suggest_company_sub_domain_name(company_name)
#             return JsonResponse({'suggested_company_sub_domain_name': suggested_company_sub_domain_name}, status=HTTPStatus.HTTP_200_OK)

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
#                         customer_company_details.save()

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
#                         customer_company_details.save()



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

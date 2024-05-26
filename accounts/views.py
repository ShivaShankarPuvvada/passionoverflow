from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth import get_user_model

from django_countries import countries
from .models import GENDER_IN_CHOICES, CustomerCompanyDetails, Company
from django.db.models import Q

from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError


# User = get_user_model()

# # Create your views here.
# class CustomerCompanyVerificationView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request):
#         try:
#             data=request.data
#             must_keys=["company_name_or_sub_domain"]
#             if bool(set(must_keys)-set(data.keys())):
#                 return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)

#             company_name_or_sub_domain = data.get('company_name_or_sub_domain')
#             customer_company_object = Company.objects.filter(Q(name=company_name_or_sub_domain) | Q(sub_domain_name=company_name_or_sub_domain))

#             if customer_company_object.exists():
#                 customer_company_object = customer_company_object.latest()
#                 company_name = customer_company_object.name
#                 company_sub_domain_name = customer_company_object.sub_domain_name
#                 response_data = {
#                     'data': {
#                         "company_name": company_name,
#                         "company_sub_domain_name": company_sub_domain_name,
#                         },
#                     "message": "This Company has already account. Please enter new values if this is not your company. Or Ask your administrator to invite you as contributor.",
#                 }
#                 return Response(response_data, status=status.HTTP_409_CONFLICT)
#             else:
#                 response_data = {
#                     'data': {
#                         "proceed": True,
#                         },
#                     "message": "This is new data. We can proceed.",
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class UserDetailsVerificationView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request):
#         try:
#             data=request.data
#             must_keys=["email_or_phone_number_or_username"]
#             if bool(set(must_keys)-set(data.keys())):
#                 return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)

#             email_or_phone_number_or_username = data.get('email_or_phone_number_or_username')
#             user_object = User.objects.filter(Q(email=email_or_phone_number_or_username) 
#                                               | Q(phone_number=email_or_phone_number_or_username) 
#                                               | Q(username=email_or_phone_number_or_username))


#             if user_object.exists():
#                 user_object = user_object.latest()
#                 email = user_object.email
#                 phone_number = user_object.phone_number
#                 username = user_object.username
#                 response_data = {
#                     'data': {
#                         "email": email,
#                         "phone_number": phone_number,
#                         "username": username,
#                         },
#                     "message": "This User has already account Or Username already exists. Please enter new values if this is not your email or phone number. Or click on forgot password.",
#                 }
#                 return Response(response_data, status=status.HTTP_409_CONFLICT)
#             else:
#                 response_data = {
#                     'data': {
#                         "proceed": True,
#                         },
#                     "message": "This is new data. We can proceed.",
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         try:
#             data=request.data
#             must_keys=[]
#             if bool(set(must_keys)-set(data.keys())):
#                 return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)

#             serializer = UserCreationSerializer(data)
#             if serializer.is_valid():
#                 serializer.save()
#                 profile_url = reverse("accounts:profile")  # Replace "login" with the name of your login view
#                 response_data = {
#                     'data': serializer.data,
#                     "message": "Data Saved Successfully.",
#                     "profile_url": profile_url,
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)
#             else:
#                 response_data = {
#                     'data': {},
#                     "message": "No New Data Passed.",
#                     "profile_url": profile_url,
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class RegistrationView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     """
#     get method is not needed. we don't need to send anything to frontend.
#     """
#     def post(self, request):
#         try:
#             data = request.data
#             must_keys = ["username", "email", "phone_number", "gender", "country", "company_name", "company_sub_domain_name"]

#             if bool(set(must_keys) - set(data.keys())):
#                 return Response({'Message': str(set(must_keys) - set(data.keys())) + " missing"}, status=status.HTTP_400_BAD_REQUEST)

#             # Extract user data
#             user_data = {
#                 "full_name": data["full_name"],
#                 "username": data["username"],
#                 "email": data["email"],
#                 "phone_number": data["phone_number"],
#                 "gender": data["gender"],
#                 "country": data["country"],
#                 "password": data["password"],
#             }

#             # Extract company data
#             company_data = {
#                 "name": data["company_name"],
#                 "sub_domain_name": data["company_sub_domain_name"],
#             }

#             # Create User and Company instances
#             user_serializer = UserCreationSerializer(data=user_data)
#             company_serializer = CompanySerializer(data=company_data)

#             # Validate and save User and Company instances
#             if not user_serializer.is_valid() and not company_serializer.is_valid():
#                 return Response({'user_error': user_serializer.errors,'company_error': company_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 user_serializer.is_valid(raise_exception=True)
#                 user_instance = user_serializer.save()
#                 user_instance.set_password(user_instance.password)
#                 user_instance.save()
#                 company_serializer.is_valid(raise_exception=True)
#                 company_instance = company_serializer.save(created_by=user_instance)

#                 # Create CustomerCompanyDetails instance
#                 customer_company_details_instance = CustomerCompanyDetails.objects.create(
#                     company=company_instance,
#                     company_root_user=user_instance,
#                     company_user=user_instance,
#                     created_by=user_instance
#                 )

#                 login_url = reverse("accounts:login")  # for first user we need to redirect him mail verification, and after, after login.

#                 # Serialize customer company details data
#                 serialized_customer_company_details = CustomerCompanyDetailsSerializer(customer_company_details_instance).data

#                 response_data = {
#                     'user_data': user_serializer.data,
#                     'company_data': company_serializer.data,
#                     'customer_company_details_data': serialized_customer_company_details,  # Include serialized customer company details data
#                     "message": "Registration successful. Please Verify email.",
#                     "login_url": login_url,
#                 }

#                 return Response(response_data, status=status.HTTP_201_CREATED)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error)
#             return Response({'Message': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class LoginView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def get(self, request):
#         try:
#             return Response({}, status=status.HTTP_200_OK)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         try:
#             data=request.data
#             must_keys=["username", "password"]
#             if bool(set(must_keys)-set(data.keys())):
#                 return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)

#             obtain_token_instance = ObtainTokenView()
#             response_from_obtain_token = obtain_token_instance.post(request)
#             token_response_dictionary = response_from_obtain_token.data
#             access_token = token_response_dictionary['access_token']
#             refresh_token = token_response_dictionary['refresh_token']
#             user = token_response_dictionary['user']
#             user_serializer = UserResponseSerializer(user)
#             return Response({'access_token': access_token, 'refresh_token': refresh_token, 'user': user_serializer.data}, status=status.HTTP_200_OK)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class LogoutView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request):
#         try:
#             # return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
#             tokens = request.data.get("tokens")
#             if "refresh_token" in tokens:
#                 del tokens["refresh_token"]
#             return Response({"message": "Logout successful."}, status=status.HTTP_204_NO_CONTENT)
#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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
#                 return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)

#             # Check if full_name is empty
#             if not data['full_name']:
#                 return Response({'Message': 'Full name cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

#             full_name = request.data.get('full_name')
#             suggested_username = suggest_username(full_name)
#             return Response({'suggested_username': suggested_username}, status=status.HTTP_200_OK)

#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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
#                 return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)

#             # Check if company_name is empty
#             if not data['company_name']:
#                 return Response({'Message': 'Company name cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

#             company_name = request.data.get('company_name')
#             suggested_company_sub_domain_name = suggest_company_sub_domain_name(company_name)
#             return Response({'suggested_company_sub_domain_name': suggested_company_sub_domain_name}, status=status.HTTP_200_OK)

#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error) 
#             return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class GiveContributorAccessToCollaborators(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         try:
#             data = request.data
#             must_keys = ["user_ids", "company_id"]

#             # Check if required keys are present
#             if bool(set(must_keys) - set(data.keys())):
#                 return Response({'Message': str(set(must_keys) - set(data.keys())) + " missing"}, status=status.HTTP_400_BAD_REQUEST)

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

#             return Response(response_data, status=status.HTTP_200_OK)

#         except IntegrityError as integrity_error: # this error relates to database.
#             error_message = "Integrity Error: " + str(integrity_error)
#             return Response({'Message': error_message}, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error)
#             return Response({'Message': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class RemoveContributorAccess(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         try:
#             data = request.data
#             must_keys = ["user_ids", "company_id"]

#             # Check if required keys are present
#             if bool(set(must_keys) - set(data.keys())):
#                 return Response({'Message': str(set(must_keys) - set(data.keys())) + " missing"}, status=status.HTTP_400_BAD_REQUEST)

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

#             return Response(response_data, status=status.HTTP_200_OK)

#         except IntegrityError as integrity_error: # this error relates to database.
#             error_message = "Integrity Error: " + str(integrity_error)
#             return Response({'Message': error_message}, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as error:
#             error_message = "Internal Server Error: " + str(error)
#             return Response({'Message': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

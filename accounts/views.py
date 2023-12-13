from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse

from django.contrib.auth import get_user_model
from rest_framework import views, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_countries import countries
from .models import GENDER_IN_CHOICES, CustomerCompanyDetails
from django.db.models import Q

from .serializers import ObtainTokenSerializer, UserResponseSerializer, RefreshTokenSerializer, UserCreationSerializer
from .authentication import JWTAuthentication
from rest_framework.renderers import TemplateHTMLRenderer


User = get_user_model()

# Create your views here.
class ObtainTokenView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ObtainTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username_or_phone_number = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = User.objects.filter(username=username_or_phone_number).first()
        if user is None:
            user = User.objects.filter(phone_number=username_or_phone_number).first()

        if user is None:
            return Response({'message': "Sorry, but we couldn't find your information in our database. Please check the details you provided and try again, or consider signing up if you haven't already."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({'message': "Oops! It seems you've entered the wrong password. Please double-check your password and try again."}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate the JWT token
        access_jwt_token = JWTAuthentication.create_access_jwt(user)
        refresh_jwt_token = JWTAuthentication.create_refresh_jwt(user.id)

        return Response({'access_token': access_jwt_token, 'refresh_token': refresh_jwt_token, 'user': user})


# Create your views here.
class RefreshTokenView(APIView):
    """
    create_access_jwt_token_using_refresh_jwt_token
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            refresh_token = serializer.validated_data.get('refresh_token')
            
            if refresh_token == "" or refresh_token == None:
                return Response({'message': "Refresh token is empty."}, status=status.HTTP_400_BAD_REQUEST)
            
            refresh_token_payload = JWTAuthentication.decode_refresh_token(refresh_token)
            
            if "exp" not in refresh_token_payload:
                return Response({'message': "Something wrong with refresh token, expiry details can not be found. Please redirect to the login page."}, status=status.HTTP_400_BAD_REQUEST)

            refresh_token_expired = JWTAuthentication.is_token_expired(refresh_token_payload["exp"])

            if refresh_token_expired:
                return Response({'message': "Refresh token expired. Please redirect to the login page."}, status=status.HTTP_400_BAD_REQUEST)

            if "user_id" not in refresh_token_payload:
                return Response({'message': "Something wrong with refresh token, user details can not be found. Please redirect to the login page."}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(id=refresh_token_payload["user_id"]).first()

            if user is None:
                return Response({'message': "Sorry, but we couldn't find user information in our database. Please redirect to login page."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate the new access JWT token
            new_access_jwt_token = JWTAuthentication.create_access_jwt(user)
            user_serializer = UserResponseSerializer(user)
            return Response({'new_access_jwt_token': new_access_jwt_token, 'user': user_serializer.data})
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CustomerCompanyVerificationView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        try:
            data=request.data
            must_keys=["company_name_or_sub_domain"]
            if bool(set(must_keys)-set(data.keys())):
                return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)
            
            company_name_or_sub_domain = data.get('company_name_or_sub_domain')
            customer_company_object = CustomerCompanyDetails.objects.filter(Q(company_name=company_name_or_sub_domain) | Q(company_sub_domain_name=company_name_or_sub_domain))


            if customer_company_object.exists():
                customer_company_object = customer_company_object.latest()
                company_name = customer_company_object.company_name
                company_sub_domain_name = customer_company_object.company_sub_domain_name
                response_data = {
                    'data': {
                        "company_name": company_name,
                        "company_sub_domain_name": company_sub_domain_name,
                        },
                    "message": "This Company has already account. Please enter new values if this is not your company. Or click on forgot password.",
                }
                return Response(response_data, status=status.HTTP_409_CONFLICT)
            else:
                response_data = {
                    'data': {
                        "proceed": True,
                        },
                    "message": "This is new data. We can proceed.",
                }
                return Response(response_data, status=status.HTTP_200_OK)

        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserDetailsVerificationView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        try:
            data=request.data
            must_keys=["email_or_phone_number_or_username"]
            if bool(set(must_keys)-set(data.keys())):
                return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)
            
            email_or_phone_number_or_username = data.get('email_or_phone_number_or_username')
            user_object = User.objects.filter(Q(email=email_or_phone_number_or_username) 
                                              | Q(phone_number=email_or_phone_number_or_username) 
                                              | Q(username=email_or_phone_number_or_username))


            if user_object.exists():
                user_object = user_object.latest()
                email = user_object.email
                phone_number = user_object.phone_number
                username = user_object.username
                response_data = {
                    'data': {
                        "email": email,
                        "phone_number": phone_number,
                        "username": username,
                        },
                    "message": "This User has already account Or Username already exists. Please enter new values if this is not your email or phone number. Or click on forgot password.",
                }
                return Response(response_data, status=status.HTTP_409_CONFLICT)
            else:
                response_data = {
                    'data': {
                        "proceed": True,
                        },
                    "message": "This is new data. We can proceed.",
                }
                return Response(response_data, status=status.HTTP_200_OK)

        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        try:
            # Retrieve country data from django-countries
            country_data = [{'code': code, 'name': name} for code, name in list(countries)]
            response_data = {
                'countries': country_data,
                'genders': GENDER_IN_CHOICES,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data=request.data
            must_keys=[]
            if bool(set(must_keys)-set(data.keys())):
                return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)

            serializer = UserCreationSerializer(data)
            if serializer.is_valid():
                serializer.save()
                profile_url = reverse("accounts:profile")  # Replace "login" with the name of your login view
                response_data = {
                    'data': serializer.data,
                    "message": "Data Saved Successfully.",
                    "profile_url": profile_url,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'data': {},
                    "message": "No New Data Passed.",
                    "profile_url": profile_url,
                }
                return Response(response_data, status=status.HTTP_200_OK)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RegistrationView(APIView):
    renderer_classes = [TemplateHTMLRenderer,]
    template_name = "accounts/signup.html"
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        try:
            # Retrieve country data from django-countries
            country_data = [{'code': code, 'name': name} for code, name in list(countries)]
            response_data = {
                'countries': country_data,
                'genders': GENDER_IN_CHOICES,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data=request.data
            must_keys=["username", "email", "phone_number", "gender", "country"]
            if bool(set(must_keys)-set(data.keys())):
                return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)

            serializer = UserCreationSerializer(data)
            if serializer.is_valid():
                serializer.save()
                # Assuming registration was successful, generate the login URL in Django format.
                login_url = reverse("accounts:login")  # Replace "login" with the name of your login view
                response_data = {
                    'data': serializer.data,
                    "message": "Registration successful. Please log in.",
                    "login_url": login_url,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            return Response({}, status=status.HTTP_200_OK)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data=request.data
            must_keys=["username", "password"]
            if bool(set(must_keys)-set(data.keys())):
                return Response({'Message':str(set(must_keys)-set(data.keys()))+" missing"},status=status.HTTP_400_BAD_REQUEST)


            obtain_token_instance = ObtainTokenView()
            response_from_obtain_token = obtain_token_instance.post(request)
            token_response_dictionary = response_from_obtain_token.data
            access_token = token_response_dictionary['access_token']
            refresh_token = token_response_dictionary['refresh_token']
            user = token_response_dictionary['user']
            user_serializer = UserResponseSerializer(user)
            return Response({'access_token': access_token, 'refresh_token': refresh_token, 'user': user_serializer.data}, status=status.HTTP_200_OK)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            # return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            tokens = request.data.get("tokens")
            if "refresh_token" in tokens:
                del tokens["refresh_token"]
            return Response({"message": "Logout successful."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            error_message = "Internal Server Error: " + str(error) 
            return Response({'Message': error_message }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

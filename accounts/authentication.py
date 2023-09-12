
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from datetime import datetime

from rest_framework.exceptions import AuthenticationFailed, ParseError

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract the JWT from the Authorization header
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        if jwt_token is None:
            return None

        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)  # clean the token
        # Decode the JWT and verify its signature
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except:
            raise AuthenticationFailed("Something wrong with the token. Redirect to login.")
        
        token_expired = JWTAuthentication.is_token_expired(payload["exp"])

        if token_expired:
            raise AuthenticationFailed("Access Token Expired. Redirect to login.")

        # Get the user from the database
        username_or_phone_number = payload.get('user_identifier')
        if username_or_phone_number is None:
            raise AuthenticationFailed('User identifier not found in JWT')

        user = User.objects.filter(username=username_or_phone_number).first()
        if user is None:
            user = User.objects.filter(phone_number=username_or_phone_number).first()
            if user is None:
                raise AuthenticationFailed('User not found')

        # Return the user and token payload
        return user, payload

    def authenticate_header(self, request):
        return 'Bearer'

    @classmethod
    def create_access_jwt(cls, user):
        # Create the JWT payload
        payload = {
            'user_id': user.id,
            'user_identifier': user.username,
            'exp': int((datetime.now() + settings.JWT_CONF['ACCESS_TOKEN_LIFETIME']).timestamp()),
            # set the expiration time for 1 hour from now
            'iat': datetime.now().timestamp(),
            'username': user.username,
            'phone_number': user.phone_number,
        }

        # Encode the JWT with your secret key
        access_jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return access_jwt_token
    
    @classmethod
    def create_refresh_jwt(cls, user_id):
        # Create the JWT payload
        payload = {
            'user_id': user_id,
            'exp': int((datetime.now() + settings.JWT_CONF['REFRESH_TOKEN_LIFETIME']).timestamp()),
            'type': 'refresh',
        }

        # Encode the JWT with your secret key
        refresh_jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return refresh_jwt_token
    
    @classmethod
    def decode_refresh_token(cls, refresh_token):
        # Decode the Refresh JWT token and verify its signature
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except:
            raise ParseError()
        return payload


    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace('Bearer', '').replace(' ', '')  # clean the token
        return token
    

    @classmethod
    def is_token_expired(cls, expiration_timestamp):
        try:
            expiration_datetime = datetime.fromtimestamp(expiration_timestamp)
            # Compare the expiration time to the current time
            if expiration_datetime < datetime.now():
                return True  # Token has expired
            else:
                return False  # Token is still valid
        except Exception:
            return True  # Other exceptions (e.g., token is not a JWT)

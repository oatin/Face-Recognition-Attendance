from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from urllib.parse import parse_qs
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        
        token = None
        
        if 'token' in query_params:
            token = query_params['token'][0]
        elif 'headers' in scope:
            headers = dict(scope['headers'])
            if b'authorization' in headers:
                auth_header = headers[b'authorization'].decode()
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
        
        if token:
            scope['user'] = await self.get_user(token)
        else:
            scope['user'] = AnonymousUser()
            
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, token):
        try:
            validated_token = AccessToken(token)
            user_id = validated_token.get('user_id')
            
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist, jwt.PyJWTError):
            return AnonymousUser()
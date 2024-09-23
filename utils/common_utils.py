import os

import jwt
import datetime

def create_jwt_token(account_id):
    payload = {
        'account_id': account_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=5)  # Token expiration time
    }
    secret_key = os.getenv('SECRET_KEY')
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token
# g is the global object which is used to pass the user globally on authentication
from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

import models

token_auth = HTTPTokenAuth(scheme='Token')
basic_auth = HTTPBasicAuth()
auth = MultiAuth(token_auth, basic_auth)


@basic_auth.verify_password
def verify_password(email_or_username, password):
    try:
        user = models.User.get(
            (models.User.email == email_or_username) |
            (models.User.username == email_or_username)
        )
        if not user.verify_password(password):
            return False
    except models.User.DoesNotExist:
        return False
    else:
        g.user = user
        return True


@token_auth.verify_token
def verify_token(token):
    user = models.User.verify_auth_token(token)
    if user is not None:
        g.user = user
        return True
    return False

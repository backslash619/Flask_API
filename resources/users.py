import json

from flask import Blueprint, make_response, url_for
from flask_restful import (Resource, Api,
                           reqparse, fields, marshal)

import models

users_fields = {
    'username': fields.String,
    'email':fields.String,
    'password':fields.String
}


class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required=True,
            help='No email provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=True,
            help='No password provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'verify_password',
            required=True,
            help='No password verification provided',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        users = [marshal(user, users_fields)
                 for user in models.User.select()]
        return {'users': users}

    def post(self):
        args = self.reqparse.parse_args()
        if args.get('password') == args.get('verify_password'):
            user = models.User.create_user(**args)
            return marshal(user, users_fields), 201
        return make_response(
            json.dumps(
                {
                    'error': 'Password password verification does not match.'
                }
            ), 400)


users_api = Blueprint('resources.users', __name__)
api = Api(users_api)
api.add_resource(
    UserList,
    '/users',
    endpoint='users'
)

import json

from flask import Blueprint, url_for, g, make_response
from flask_restful import (Resource, Api,
                           reqparse, inputs, fields, marshal_with, abort)

import models
from auth import auth

review_fields = {
    'id': fields.Integer,
    'for_course': fields.String,
    'rating': fields.Integer,
    'comment': fields.String(default=''),
    'created_at': fields.DateTime
}


def review_or_404(review_id):
    try:
        review = models.Review.get(models.Review.id == review_id)
    except models.Review.DoesNotExist:
        abort(404)
    else:
        return review


def add_course(review):
    review.for_course = [url_for('resources.courses.course', id=review.course.id)]
    return review


class ReviewList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'course',
            required=True,
            type=inputs.positive,
            # has to be +ve number
            help='No course provided.',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'rating',
            required=True,
            type=inputs.int_range(1, 5),
            help='No rating provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'comment',
            required=True,
            help='No rating provided',
            default='',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(review_fields)
    def get(self):
        reviews = [add_course(review) for review in models.Review.select()]
        return {'reviews': reviews}

    @marshal_with(review_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        review = models.Review.create(
            created_by=g.user,
            **args
        )
        return (add_course(review), 201,
                {
                    'Location': url_for('resources.reviews.review', id=review.id)
                })


class Review(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'rating',
            required=True,
            type=inputs.int_range(1, 5),
            help='No rating provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'comment',
            required=True,
            help='No rating provided',
            default='',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(review_fields)
    def get(self, id):
        return add_course(review_or_404(id))

    @marshal_with(review_fields)
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            review = models.Review.select().where(
                models.Review.created_by == g.user,
                models.Review.id == id
            ).get()
        except models.Review.DoesNotExist:
            return make_response(
                json.dumps(
                    {
                        'error': 'that review does not exists or not editable.'
                    }
                ), 403
            )
        query = review.update(**args)
        query.execute()
        review = add_course(review_or_404(id))
        return ('Review Updated!!', review, 200,
                {'Location': url_for('resources.reviews.review', id=id)})

    @auth.login_required
    def delete(self, id):
        try:
            review = models.Review.select().where(
                models.Review.created_by == g.user,
                models.Review.id == id
            ).get()
        except models.Review.DoesNotExist:
            return make_response(
                json.dumps(
                    {
                        'error': 'that review does not exists or not editable.'
                    }
                ), 403
            )
        query = review.delete()
        query.execute()
        return ('Review Deleted!!', 204,
                {'Location': url_for('resources.reviews')})


# making a blueprint
reviews_api = Blueprint('resources.reviews', __name__)
api = Api(reviews_api)
api.add_resource(
    ReviewList,
    '/reviews',
    endpoint='reviews'
)
api.add_resource(
    Review,
    '/reviews/<int:id>',
    endpoint='review'
)

# after this register the endpoints with the app in app.py

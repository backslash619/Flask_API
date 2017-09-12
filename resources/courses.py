from flask import Blueprint, url_for
from flask_restful import (Resource, Api,
                           reqparse, inputs,
                           fields, marshal,
                           abort, marshal_with)

import models
from auth import auth

# definfing the fields as on response we send the formatted data
course_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'url': fields.String,
    'reviews': fields.List(fields.String)
}


# adding the reviews
def add_reviews(course):
    # url path is the getting to the endpoint of review
    course.reviews = [url_for('resources.reviews.review', id=review.id)
                      for review in course.review_set]
    return course


def course_or_404(course_id):
    try:
        course = models.Course.get(models.Course.id == course_id)
    except models.Course.DoesNotExist:
        abort(404)
    else:
        return course


class CourseList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No course title provided.',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'url',
            required=True,
            help='No course url provided or bad url provided .',
            location=['form', 'json'],
            type=inputs.url
        )
        super().__init__()

    def get(self):
        courses = [marshal(add_reviews(course), course_fields)
                   for course in models.Course.select()]
        return {'courses': courses}

    @marshal_with(course_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        # args is basically the dict of all these arguments
        course = models.Course.create(**args)
        return add_reviews(course)


class Course(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No course title provided.',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'url',
            required=False,
            help='No course url provided or bad url provided .',
            location=['form', 'json'],
            type=inputs.url
        )
        super().__init__()

    @marshal_with(course_fields)
    def get(self, id):
        return add_reviews(course_or_404(id))

    @marshal_with(course_fields)
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.Course.update(**args).where(models.Course.id == id)
        query.execute()
        return ('Course Updated!!', add_reviews(course_or_404(id)), 200,
                {'Location': url_for('resources.courses.course', id=id)})

    @auth.login_required
    def delete(self, id):
        query = models.Course.delete().where(models.Course.id == id)
        query.execute()
        return 'Course deleted!!!', 200, {'Location': url_for('resources.courses')}


# making a blueprint

courses_api = Blueprint('resources.courses', __name__)
# basically we pass an app in Api as courses _api is just
# a proxy not a actual app
api = Api(courses_api)
# adding resources
api.add_resource(
    CourseList,
    '/api/v1/courses',
    endpoint='courses'
)
api.add_resource(
    Course,
    '/api/v1/courses/<int:id>',
    endpoint='course'
)
# after this register the endpoints with the app in app.py

from flask_argon2 import Argon2
from peewee import SqliteDatabase

DATABASE = SqliteDatabase('courses.sqlite')
HASHER = Argon2()

DEBUG = True
HOST = '0.0.0.0'
PORT = 8000
SECRET_KEY = 'fskhiudpoad-0qwJFOIFUOofi8t893fewqvnsdk`2iu09wd0,qwlkejw.v/.c,blv98;s,fdl'
DEFAULT_RATE = "10/hour"

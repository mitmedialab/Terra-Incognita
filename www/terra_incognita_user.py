#	User class to handle login and some other stuff
from flask_login import UserMixin
import time


class TIUser(UserMixin):

	def __init__(self, attributes):
		for key in attributes:
			setattr(self, key, attributes[key])
	def __repr__(self):
		return '<User %r>' % self.username

	def get_id(self):
		return str(self._id)


def get_user_from_DB_row(row):
	return TIUser(row)


def create_new_user(service, service_id, username):
	fields = {}
	fields['service'] = service
	fields['service_id'] = service_id
	fields['username'] = username
	fields['firstLoginDate'] = time.time() * 1000
	fields['lastLoginDate'] = time.time() * 1000

	return TIUser(fields)

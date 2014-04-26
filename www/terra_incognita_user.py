#	User class to handle login and some other stuff
from flask.ext.login import UserMixin
import time


class TIUser(UserMixin):

	def __init__(self, attributes):
		for key in attributes:
			setattr(self, key, attributes[key])
	def __repr__(self):
		return '<User %r>' % self.email

	def get_id(self):
		return str(self._id)


def get_user_from_DB_row(row):
	return TIUser(row)
					

def create_new_user(email):
	t = email.split('@')
	stuff = {}
	stuff["email"] = email
	stuff["username"] = t[0]
	stuff["firstLoginDate"] = time.time() * 1000
	stuff["lastLoginDate"] = time.time() * 1000

	return TIUser(stuff)

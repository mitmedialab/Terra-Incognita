#	User class to handle login and some other stuff
from flask.ext.login import UserMixin
import datetime


class User(UserMixin):

	def __init__(self, email, **kwargs):
		log.debug("user.py >> __init__")
		self.email = email
		if (kwargs.get("_id") is not None):
			self._id = kwargs.get("_id")
		self.firstLoginDate = kwargs.get("firstLoginDate")
		self.lastLoginDate = kwargs.get("lastLoginDate")
		self.username = kwargs.get("username")
		
		
	def __repr__(self):
		return '<User %r>' % self.email

	def get_id(self):
		return str(self._id)


def get_user_from_DB_row(row):
	return User(	row['email'],
					_id=row["_id"],
					firstLoginDate=row["firstLoginDate"],
					lastLoginDate=row["lastLoginDate"],
					username=row["username"])
					

def create_new_user(email):
	log.debug("user.py >> create_new_user")
	t = email.split('@')
	herUsername = t[0]
	return User(email, firstLoginDate=datetime.datetime.utcnow(), lastLoginDate=datetime.datetime.utcnow(), username=herUsername)

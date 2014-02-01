#	User class to handle login and some other stuff
from flask.ext.login import UserMixin
import datetime


class User(UserMixin):

	def __init__(self, email, **kwargs):
		self.email = email
		if (kwargs.get("_id") is not None):
			self._id = kwargs.get("_id")
		self.firstLoginDate = kwargs.get("firstLoginDate")
		self.lastLoginDate = kwargs.get("lastLoginDate")
		self.currentLevel = kwargs.get("currentLevel")
		
	def __repr__(self):
		return '<User %r>' % self.email

	def get_id(self):
		return str(self._id)


def get_user_from_DB_row(row):
	return User(	row['email'],
					_id=row["_id"],
					firstLoginDate=row["firstLoginDate"],
					lastLoginDate=row["lastLoginDate"],
					currentLevel=row["currentLevel"])

def create_new_user(email):
	return User(email, firstLoginDate=datetime.datetime.utcnow(), lastLoginDate=datetime.datetime.utcnow(),currentLevel=LEVELS[0])

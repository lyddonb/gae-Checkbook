import webapp2

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
import jinja2
import os
import logging


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

ROOT_PATH  = os.path.dirname(__file__)

class Checkbook(db.Model):
	author = db.UserProperty()
	name = db.StringProperty()
	amount = db.FloatProperty()
	active = db.BooleanProperty()
	time = db.DateProperty(auto_now_add = True)

class Transaction(db.Model):
	author = db.UserProperty()
	date = db.DateTimeProperty(auto_now_add = True)
	dateDisplay = db.DateProperty(auto_now_add = True)
	debit_amount = db.FloatProperty()
	description = db.StringProperty()
	credit_amount = db.FloatProperty()
	Total = db.FloatProperty()

class Total(db.Model):
	author = db.UserProperty()
	checkbook_total = db.FloatProperty()


def get_template(name):
    return os.path.join(ROOT_PATH, name)


class MainPage(webapp2.RequestHandler):	
	def get(self):
		user = users.get_current_user()

		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			user = 'Friend'
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'username': user,
			'url': url,
			'url_linktext': url_linktext,
		}

		self.response.out.write(template.render(get_template('checkbook_main.html'), template_values))

class About(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()

		if user:
			#self.redirect('/about')
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'logout'
		else:
			user = 'Friend'
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'username': user,
			'url': url,
			'url_linktext': url_linktext,
		}

		self.response.out.write(template.render(get_template('about.html'), template_values))

class UserHandler(webapp2.RequestHandler):		
	def get(self):
		user = users.get_current_user()

		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			self.redirect('/')
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'



		checkbook = db.GqlQuery("SELECT * FROM Checkbook")
		transaction = db.GqlQuery("SELECT * FROM Transaction ORDER BY date ASC")
		totals = db.GqlQuery("SELECT * FROM Total ORDER BY author DESC")

		active = False
		Total = 0.00
		if user:
			for book in checkbook:
				if book.author == user:
					Total = book.amount
			for tran in transaction:
				if tran.author == user:
					Total = Total + tran.debit_amount
					Total = Total - tran.credit_amount
		else:
			Total = 0.00

		book_name = "No"
		if user:
			for book in checkbook:
				if book.author == user:
					book_name = book.name
					active = book.active
				else:
					book_name = "No"
		else:
			book_name = "No"



		template_values = {
			'active': active,
			'book_name': book_name,
			'total': Total,
			'checkbook': checkbook,
			'username': user,
			'url': url,
			'url_linktext': url_linktext,
			'transaction': transaction,
			'user': user,
		}

		template = jinja_environment.get_template('Userpage.html')
		self.response.out.write(template.render(template_values))


	def post(self):

		submit_checkbook = self.request.get('checkbook')
		submit_debit = self.request.get('debit')
		submit_credit = self.request.get('credit')

		user = users.get_current_user()

		TOTAL = 0.00

		if submit_checkbook:
			checkbook = Checkbook()	
			if user:
				checkbook.author = user
				checkbook.name = self.request.get('new_checkbook')
				checkbook.amount = float(self.request.get('amount', 0.0))
				checkbook.active = True
				TOTAL = checkbook.amount
				checkbook.put()
		else:
			if user:
				transaction = Transaction()
				if submit_debit:
					transaction.author = user
					transaction.debit_amount = float(self.request.get('debit_amount', 0.0))
					transaction.description = self.request.get('debit_tran_des')
					transaction.credit_amount = 0.0
					transaction.Total = TOTAL + transaction.debit_amount
					transaction.put()
				elif submit_credit:
					transaction.author = user
					transaction.credit_amount = float(self.request.get('credit_amount', 0.0))
					transaction.description = self.request.get('credit_tran_des', 0.0)
					transaction.debit_amount = 0.0
					transaction.Total = TOTAL - transaction.credit_amount
					transaction.put()

		if user:
			total = Total()
			total.author = user
			total.checkbook_total = TOTAL
			total.put()

		self.redirect('/userpage')



app = webapp2.WSGIApplication([('/', MainPage),
								('/userpage', UserHandler),
								('/about', About)], debug = True)


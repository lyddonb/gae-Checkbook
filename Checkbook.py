import logging
import os

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

import jinja2

import webapp2


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

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
    total = db.FloatProperty()


class Total(db.Model):
    author = db.UserProperty()
    checkbook_total = db.FloatProperty()


def get_template(name):
    return os.path.join(ROOT_PATH, name)


class BaseHandler(webapp2.RequestHandler):

    def set_user(self):
        self.user = users.get_current_user()

        if self.user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            self.user = 'Friend'
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'username': user,
            'url': url,
            'url_linktext': url_linktext,
        }

        return template_values

    def render_template(self, tempalte_name, ctx):
        self.response.out.write(template.render(get_template(tempalte_name),
                                                ctx))


class MainPage(BaseHandler):

    def get(self):
        ctx = self.set_user()
        self.render_template('checkbook_main.html', ctx)


class About(BaseHandler):

    def get(self):
        ctx = self.set_user()
        self.render_template('about.html', ctx)


class UserHandler(BaseHandler):

    def _get_checkbook(self):
        if not self.user:
            return

        return Checkbook.all().filter('author', self.user).get()

    def get(self):
        ctx = self.set_user()


        active = False
        total = 0.00
        book_name = "No"

        checkbook = self._get_checkbook()

        if checkbook:
            total = checkbook.amount
            transaction_query = Transaction.all().filter('author', self.user)

            for tran in transaction_query:
                total = total + tran.debit_amount
                total = total - tran.credit_amount

            book_name = book.name
            active = book.active


        ctx.update({
            'active': active,
            'book_name': book_name,
            'total': total,
            'checkbook': checkbook,
            'transaction': transaction,
            'user': user,
        })

        self.render_template('Userpage.html', ctx)

    def post(self):
        submit_checkbook = self.request.get('checkbook')
        submit_debit = self.request.get('debit')
        submit_credit = self.request.get('credit')

        user = users.get_current_user()

        if not user or not submit_checkbook:
            self.redirect('/userpage')
            return

        to_save = []

        checkbook = Checkbook()	
        checkbook.author = user
        checkbook.name = self.request.get('new_checkbook')
        checkbook.amount = float(self.request.get('amount', 0.0))
        checkbook.active = True
        total_value = checkbook.amount

        transaction = Transaction()
        transaction.author = user

        if submit_debit:
            transaction.debit_amount = float(
                self.request.get('debit_amount', 0.0))
            transaction.description = self.request.get('debit_tran_des')
            transaction.credit_amount = 0.0
            transaction.total = total_value + transaction.debit_amount

            to_save.append(transaction)

        elif submit_credit:
            transaction.credit_amount = float(
                self.request.get('credit_amount', 0.0))
            transaction.description = self.request.get('credit_tran_des', 0.0)
            transaction.debit_amount = 0.0
            transaction.total = total_value - transaction.credit_amount

            to_save.append(transaction)

        total = Total()
        total.author = user
        total.checkbook_total = total_value

        db.put([checkbook, total] + to_save)

        self.redirect('/userpage')



app = webapp2.WSGIApplication([('/', MainPage),
                               ('/userpage', UserHandler),
                               ('/about', About)], debug = True)



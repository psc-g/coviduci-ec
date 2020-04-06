from absl import logging
import collections
import json
import os.path
import tornado.escape
import tornado.web
import tornado.template
from coviduci.www.handlers import base
from coviduci import config


def get_color(value):
  color = 'red'
  if value < 0.5:
    color = 'green'
  elif value < 0.8:
    color = 'orange'
  return color


class HomeHandler(base.BaseHandler):

  ROUTE = '/'

  def initialize(self, config, db):
    self.config = config
    self.db = db
    loader = tornado.template.Loader(self.get_template_path())

  @tornado.web.authenticated
  def get(self):
    data = {'user': 'none'}
    if not self.current_user:
      self.redirect('/login', **data)
      return
    data['user'] = tornado.escape.xhtml_escape(self.current_user)
    data['display_name'] = self.db.get_display_name(data['user'])
    self.render('index.html', **data)


class LoginHandler(base.BaseHandler):

    ROUTE = '/login'

    def initialize(self, token_encoder, db):
      self.db = db
      self.token_encoder = token_encoder

    def get(self):
      status = self.get_query_argument('status', default=None)
      self.render('login.html', user='none', status=status)

    def post(self):
      user = self.get_argument('user')
      clave = self.get_argument('clave')
      user = self.db.check_login(user, self.token_encoder.encode(clave))
      if user is not None:
        self.set_secure_cookie('user', user)
        self.redirect('/')
      else:
        self.redirect('/login?status=wrong_login')


class UpdateLoginHandler(base.BaseHandler):

    ROUTE = '/update_login'

    def initialize(self, token_encoder, db):
      self.db = db
      self.token_encoder = token_encoder

    def get(self):
      status = self.get_query_argument('status', default=None)
      user = tornado.escape.xhtml_escape(self.current_user)
      self.render('update_login.html', user=user, status=status)

    def post(self):
      clave_original = self.get_argument('clave_original')
      clave_nueva_1 = self.get_argument('clave_nueva_1')
      clave_nueva_2 = self.get_argument('clave_nueva_2')
      encoded_original_login = self.token_encoder.encode(clave_original)
      user = tornado.escape.xhtml_escape(self.current_user)
      user = self.db.check_login(user, encoded_original_login)
      if user is None:
        self.redirect('/update_login?status=wrong_pwd')
      elif clave_nueva_1 != clave_nueva_2:
        self.redirect('/update_login?status=mismatch')
      elif len(clave_nueva_1) < 7:
        self.redirect('/update_login?status=short')
      else:
        encoded_new_login = self.token_encoder.encode(clave_nueva_1)
        if self.db.update_login(encoded_original_login, encoded_new_login):
          self.redirect('/update_login?status=success')
        else:
          self.redirect('/update_login?status=error')


class LogoutHandler(base.BaseHandler):

    ROUTE = '/logout'

    def get(self):
      if not self.current_user:
        self.redirect('/login')
        return
      self.current_user = None
      self.clear_all_cookies()
      self.redirect('/login')

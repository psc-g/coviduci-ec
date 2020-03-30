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
      self.render('login.html', user='none')

    def post(self):
      clave = self.get_argument('clave')
      user = self.db.check_login(self.token_encoder.encode(clave))
      if user is not None:
        self.set_secure_cookie('user', user)
        self.redirect('/')
      else:
        self.redirect('/login')


class LogoutHandler(base.BaseHandler):

    ROUTE = '/logout'

    def get(self):
      if not self.current_user:
        self.redirect('/login')
        return
      self.current_user = None
      self.clear_all_cookies()
      self.redirect('/login')

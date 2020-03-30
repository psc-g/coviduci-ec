from absl import logging
import json
import tornado.escape
import tornado.web
from coviduci.www.handlers import base
from coviduci.www.handlers import home
from coviduci.www import token


class ShowHandler(base.BaseHandler):
  ROUTE = '/show'

  def initialize(self, db):
    self.db = db

  async def get(self):
    """Serves the page with the data for a specific hospital."""
    if not self.current_user:
      self.redirect('/login')
      return
    user = tornado.escape.xhtml_escape(self.current_user)
    input_data = {'user': user}

    data = self._get_data(input_data['user'], aggregated=True)
    data.update(input_data)
    data['display_name'] = self.db.get_display_name(data['user'])

    self.set_secure_cookie(self.COOKIE, user)
    self.render('show.html', **data)

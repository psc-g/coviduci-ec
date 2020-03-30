import tornado.escape
import tornado.web
from coviduci.www.handlers import base


class MindHandler(base.BaseHandler):

  ROUTE = '/mindfulness'

  def initialize(self):
    pass

  def get(self):
    data = {'user': 'none'}
    if self.current_user:
      data['user'] = tornado.escape.xhtml_escape(self.current_user)
    self.render("mindfulness.html", **data)

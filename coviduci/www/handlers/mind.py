import tornado.web
from coviduci.www.handlers import base


class MindHandler(base.BaseHandler):

  ROUTE = '/mindfulness'

  def initialize(self):
    pass

  def get(self):
    self.render("mindfulness.html")

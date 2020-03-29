import tornado.web
from coviduci.www.handlers import base


class ResearchHandler(base.BaseHandler):

  ROUTE = '/investigacion'

  def initialize(self):
    pass

  def get(self):
    self.render("investigacion.html")


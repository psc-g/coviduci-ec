import tornado.web


class BaseHandler(tornado.web.RequestHandler):
  """A base class for handlers."""

  COOKIE = 'id'
  pages = {}  # TODO(psc): Add support for proper highlighting active page.

  def get_template_path(self):
    return 'coviduci/www/templates/'

  def get_current_user(self):
    return self.get_secure_cookie(self.COOKIE)

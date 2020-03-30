from absl import logging
import tornado.web
from coviduci.www.handlers import base
from coviduci.www.handlers import show
from coviduci.www import token


class UpdateHandler(base.BaseHandler):

  ROUTE = '/update'

  def initialize(self, db, queue):
    self.db = db
    self.queue = queue

  async def get(self):
    """Serves the page with a form to be filled by the user."""
    if not self.current_user:
      self.redirect('/login')
      return
    user = tornado.escape.xhtml_escape(self.current_user)
    input_data = {'user': user}

    data = self._get_data(input_data['user'], aggregated=False)
    data.update(input_data)
    data['display_name'] = self.db.get_display_name(data['user'])

    self.render('update_form.html', **data)

  async def post(self):
    def parse(param):
      parts = param.split('=')
      value = int(parts[1]) if parts[1].isnumeric() else parts[1]
      return parts[0], value

    data = dict([parse(p) for p in self.request.body.decode().split('&')])
    await self.queue.put(data)
    self.redirect('{}?id={}'.format(show.ShowHandler.ROUTE, data['user']))

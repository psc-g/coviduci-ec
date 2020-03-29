from absl import logging
import tornado.web
from coviduci.www.handlers import base
from coviduci.www.handlers import show
from coviduci.www import token


class UpdateHandler(base.BaseHandler):

  ROUTE = '/update'
  QUERY_ARG = 'id'

  def initialize(self, db, queue, token_encoder):
    self.db = db
    self.queue = queue
    self.token_encoder = token_encoder

  async def get(self):
    """Serves the page with a form to be filled by the user."""
    user_token = self.get_query_argument(self.QUERY_ARG)
    # TODO(psc): actually encode/decode this!
    #input_data = self.token_encoder.decode(user_token)
    input_data = {'hospital': user_token}
    if input_data is None:
      return self.redirect('/error')

    data = self._get_data(input_data['hospital'], aggregated=False)
    data.update(input_data)

    self.set_secure_cookie(self.COOKIE, user_token)
    self.render('update_form.html', **data)

  async def post(self):
    def parse(param):
      parts = param.split('=')
      value = int(parts[1]) if parts[1].isnumeric() else parts[1]
      return parts[0], value

    data = dict([parse(p) for p in self.request.body.decode().split('&')])
    #data.update(self.token_encoder.decode(self.get_secure_cookie(self.COOKIE)))
    await self.queue.put(data)
    self.redirect('{}?id={}'.format(show.ShowHandler.ROUTE, data['hospital']))

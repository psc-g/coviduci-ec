from absl import logging
import json
import tornado.web
from coviduci.www.handlers import base
from coviduci.www.handlers import home
from coviduci.www import token



class ShowHandler(base.BaseHandler):
  ROUTE = '/show'
  QUERY_ARG = 'id'

  def initialize(self, db):
    self.db = db

  async def get(self):
    """Serves the page with the data for a specific hospital."""
    user_token = self.get_query_argument(self.QUERY_ARG)
    # TODO(psc): actually encode/decode this!
    #input_data = self.token_encoder.decode(user_token)
    input_data = {'hospital': user_token}
    if input_data is None:
      return self.redirect('/error')

    data = self._get_data(input_data['hospital'], aggregated=True)
    data.update(input_data)

    logging.info('Data to show: {}'.format(data))
    self.set_secure_cookie(self.COOKIE, user_token)
    self.render("show.html", **data)

from absl import logging
import json
import time
import tornado.web
from coviduci.www.handlers import base
from coviduci.www.handlers import show
from coviduci.www import token


def time_ago(ts) -> str:
  if ts is None:
    return 'jamás'

  delta = int(time.time() - int(ts))
  units = [(86400, 'día'), (3600, 'hora'), (60, 'minuto'), (1, 'segundo')]
  for unit, name in sorted(units, reverse=True):
    curr = delta // unit
    if curr > 0:
      plural = '' if curr == 1 else 's' # hack
      return 'hace {} {}{}'.format(curr, name, plural)
  return 'ahorita'

 
TABLES = ['camas', 'personal', 'insumos', 'medicaciones', 'pacientes']


class UpdateHandler(base.BaseHandler):

  ROUTE = '/update'
  QUERY_ARG = 'id'

  def initialize(self, db, queue, token_encoder):
    self.db = db
    self.queue = queue
    self.token_encoder = token_encoder

  def get_data(self, hospital, def_val=0):
    df = self.db.get_data('hospitales')
    df = df.set_index('hospital')
    for table in TABLES:
      table_data = self.db.get_data(table)
      df = df.join(table_data.set_index('hospital'), rsuffix='.{}'.format(table))
    df = df.reset_index()
    # Since 'camas' is the first table, it will not have had a suffix appended to it.
    df = df.rename(columns={'timestamp': 'timestamp.camas'})

    try:
      data = None
      last_update = None
      for index, row in df[df.hospital == hospital].iterrows():
        data = row.to_dict()
        last_update = max([data['timestamp.{}'.format(t)] for t in TABLES])
        break
    except Exception as e:
      logging.error(e)
      data = {x: def_val for x in data.columns.to_list()}

    if data is None:
      data = {x: def_val for x in data.columns.to_list()}

    for k in data:
      if data[k] is None:
        data[k] = def_val

    data['last_update'] = time_ago(last_update)
    return data

  async def get(self):
    """Serves the page with a form to be filled by the user."""
    user_token = self.get_query_argument(self.QUERY_ARG)
    #input_data = self.token_encoder.decode(user_token)
    # TODO(psc): remove!
    input_data = {'hospital': user_token}
    if input_data is None:
      return self.redirect('/error')

    data = self.get_data(input_data['hospital'])
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
    self.redirect(show.ShowHandler.ROUTE)

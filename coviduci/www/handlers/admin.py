import tornado.web
from coviduci.www.handlers import base
from coviduci.www import token


TEST_HOSPITALS = ['Administrador', 'Primero', 'Segundo', 'Tercero']


class AddHospitalHandler(base.BaseHandler):

  ROUTE = '/add_hospital'

  def initialize(self, db, queue, token_encoder):
    self.db = db
    self.queue = queue
    self.token_encoder = token_encoder

  async def get(self):
    """Serves the page to add a hospital."""
    if not self.current_user:
      self.redirect('/login')
      return
    user = tornado.escape.xhtml_escape(self.current_user)
    if user != 'admin':
      self.redirect('/login')
      return
    self.render('add_hospital.html', user='admin')

  async def post(self):
    def parse(param):
      parts = param.split('=')
      value = int(parts[1]) if parts[1].isnumeric() else parts[1]
      return parts[0], value

    data = dict([parse(p) for p in self.request.body.decode().split('&')])
    await self.queue.put(data)
    self.redirect(ListHospitalsHandler.ROUTE)


class ListHospitalsHandler(base.BaseHandler):

  ROUTE = '/list_hospitals'

  def initialize(self, db):
    self.db = db

  async def get(self):
    """Serves the page to list all hospitals."""
    if not self.current_user:
      self.redirect('/login')
      return
    user = tornado.escape.xhtml_escape(self.current_user)
    if user != 'admin':
      self.redirect('/login')
      return
    hospitals = self.db.get_hospitals()
    hospitals = [h for h in hospitals if h not in TEST_HOSPITALS]
    data = {'user': 'admin', 'hospitals': hospitals}
    self.render('list_hospitals.html', **data)

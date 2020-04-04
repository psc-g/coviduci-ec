from absl import logging
import tornado.web
from coviduci.www.handlers import base
from coviduci.www import token


TEST_HOSPITALS = ['Ministerio de Salud', 'Administrador',
                  'Primero', 'Segundo', 'Tercero']


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
      self.redirect('/')
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
    if user != 'admin' and user != 'ministerio':
      self.redirect('/')
      return
    hospitals = self.db.get_hospitals()
    hospitals = [h for h in hospitals if h not in TEST_HOSPITALS]
    hospitals.sort()
    data = {'user': user, 'hospitals': hospitals}
    self.render('list_hospitals.html', **data)


class AllDataHandler(base.BaseHandler):
  ROUTE = '/datos_completos'

  def initialize(self, db):
    self.db = db

  def _get_all_data(self):
    df = self.db.get_data('users')
    hospitales = []
    data = {'display_name': {}, 'actualizaciones': {}}
    for hospital in df.name:
      display_name = df[df.name == hospital].display_name.to_list()[0]
      if display_name in TEST_HOSPITALS:
        continue
      hospitales.append(hospital)
      data['display_name'][hospital] = display_name
    for field in self.DEFAULT_VALUES:
      data[field] = {'total': 0}
    category_counts = {}
    for category in self.REQUIRED_CATEGORIES:
      data[category] = {}
      category_counts[category] = 0
    hospitales_df = self.db.get_data('hospitales')
    tables_df = {}
    for table in self.TABLES:
      tables_df[table] = self.db.get_data(table)
    for hospital in hospitales:
      hospital_df = hospitales_df[hospitales_df.hospital == hospital]
      if hospital_df.empty:
        continue
      hospital_df = (
          hospital_df[hospital_df.timestamp == max(hospital_df.timestamp)])
      data['actualizaciones'][hospital] = int(hospital_df.timestamp)
      for field in self.DEFAULT_VALUES:
        data[field]['total'] += int(hospital_df[field])
        data[field][hospital] = int(hospital_df[field])
      for category in self.REQUIRED_CATEGORIES:
        data[category][hospital] = []
      for table in self.TABLES:
        table_df = tables_df[table]
        table_df = table_df[table_df.hospital == hospital]
        if table_df.empty:
          continue
        for field in self.REQUIRED_FIELDS[table]:
          category = None
          max_ts = 0
          for cat in self.REQUIRED_CATEGORIES:
            if not table_df[table_df[cat] == field].empty:
              if max(table_df[table_df[cat] == field].timestamp) > max_ts:
                max_ts = max(table_df[table_df[cat] == field].timestamp)
                category = cat
          if category is not None:
            data[category][hospital].append(field)
            category_counts[category] += 1
            data['actualizaciones'][hospital] = max(
                data['actualizaciones'][hospital], max_ts)
          else:
            data['n_a'][hospital].append(field)
            category_counts['n_a'] += 1
    for hospital in data['actualizaciones']:
      data['actualizaciones'][hospital] = self._time_ago(
          data['actualizaciones'][hospital])
    for category in self.REQUIRED_CATEGORIES:
      if category_counts[category] == 0:
        data[category] = None
    return data

  async def get(self):
    """Serves the page with aggregate data for all hospitals."""
    if not self.current_user:
      self.redirect('/login')
      return
    user = tornado.escape.xhtml_escape(self.current_user)
    if user != 'admin' and user != 'ministerio':
      self.redirect('/')
      return
    data = self._get_all_data()
    data['user'] = user
    self.render('datos_completos.html', **data)

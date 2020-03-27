from absl import logging
import json
import tornado.web
from coviduci.www.handlers import base
from coviduci.www.handlers import home
from coviduci.www import token


class DataJson(tornado.web.RequestHandler):
    ROUTE = '/data'

    def initialize(self, db):
        self.db = db

    def get(self):
        data = self.db.get_data('hospitales')
        data = data.set_index('hospital')
        for table in ['camas', 'personal', 'insumos', 'medicaciones', 'pacientes']:
          table_data = self.db.get_data(table)
          data = data.join(table_data.set_index('hospital'), rsuffix='.{}'.format(table))
        data = data.reset_index()
        data = data.to_dict(orient='records')
        self.write({"data": data})


class ShowHandler(base.BaseHandler):
    ROUTE = '/show'

    def initialize(self, db):
        self.db = db

    async def get(self):
        """Serves the page with a form to be filled by the user."""
        self.render("show.html")

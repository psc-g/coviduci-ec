from absl import logging
import os.path
import tornado.ioloop
from tornado import queues
import tornado.web

from coviduci.db import queue_writer
from coviduci.db import sqlite
from coviduci.www import token
from coviduci.www.handlers import db
from coviduci.www.handlers import home
from coviduci.www.handlers import mind
from coviduci.www.handlers import show
from coviduci.www.handlers import update


class WWWServer:
  """Serves and manipulates the ICUBAM data."""

  def __init__(self, config, port):
    self.config = config
    self.port = port
    self.routes = []
    self.token_encoder = token.TokenEncoder(self.config)
    self.writing_queue = queues.Queue()
    self.db = sqlite.SQLiteDB(self.config.db.sqlite_path)
    self.make_app()
    self.callbacks = [
      queue_writer.QueueWriter(self.writing_queue, self.db)
    ]

  def add_handler(self, handler, **kwargs):
    route = os.path.join('/', handler.ROUTE)
    self.routes.append((route, handler, kwargs))
    logging.info('{} serving on {}'.format(handler.__name__, route))

  def make_app(self):
    self.add_handler(
      update.UpdateHandler, db=self.db, queue=self.writing_queue,
      token_encoder=self.token_encoder)
    self.add_handler(home.HomeHandler, config=self.config, db=self.db)
    self.add_handler(show.ShowHandler, db=self.db)
    self.add_handler(show.DataJson, db=self.db)
    self.add_handler(db.DBHandler, db=self.db)
    self.add_handler(mind.MindHandler)
    self.routes.append(
      (r"/static/(.*)",
      tornado.web.StaticFileHandler,
      {"path": "coviduci/www/static/"})
    )

  def run(self):
    logging.info('Running {} on port {}'.format(
      self.__class__.__name__, self.port))

    settings = {
      "cookie_secret": self.config.SECRET_COOKIE,
      "login_url": "/error",
    }
    app = tornado.web.Application(self.routes, **settings)
    app.listen(self.port)

    io_loop = tornado.ioloop.IOLoop.current()
    for callback_obj in self.callbacks:
      io_loop.spawn_callback(callback_obj.process)

    io_loop.start()

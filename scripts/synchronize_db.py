"""Script to pull data from spreadsheet and populate SQLite database."""
from absl import app
from absl import flags
from coviduci import config
from coviduci.db import sqlite
from coviduci.db import gsheets
from coviduci.db import synchronizer

flags.DEFINE_string("config", "resources/config.toml", "Config file.")
flags.DEFINE_string("dotenv_path", "resources/.env", "Config file.")
flags.DEFINE_enum("mode", "dev", ["prod", "dev"], "Run mode.")
FLAGS = flags.FLAGS


def main(unused_argv):
  cfg = config.Config(FLAGS.config, mode=FLAGS.mode, env_path=FLAGS.dotenv_path)
  shdb = gsheets.SheetsDB(cfg.TOKEN_LOC, cfg.SHEET_ID)
  sqldb = sqlite.SQLiteDB(cfg.db.sqlite_path)
  sync = synchronizer.Synchronizer(shdb, sqldb)
  sync.sync_hospitales()
  sync.sync_insumos()
  sync.sync_medicaciones()


if __name__ == "__main__":
  app.run(main)

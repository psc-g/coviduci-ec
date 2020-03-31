"""Script to initialize the SQLite database."""
from absl import app
from absl import flags
from coviduci import config
from coviduci.db import sqlite
from coviduci.www import token

flags.DEFINE_string('config', '/home/${USER}/resources/coviduci.toml', 'Config file.')
flags.DEFINE_string('dotenv_path', '/home/${USER}/resources/coviduci.env', 'Config file.')
FLAGS = flags.FLAGS


def main(unused_argv):
  cfg = config.Config(FLAGS.config, env_path=FLAGS.dotenv_path)
  token_encoder = token.TokenEncoder(cfg)
  sqldb = sqlite.SQLiteDB(cfg.db.sqlite_path, token_encoder)
  sqldb.create_users()


if __name__ == "__main__":
  app.run(main)

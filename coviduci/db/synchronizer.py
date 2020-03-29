"""Pulls data from the google sheet and adds it to the sqlite DB."""
from coviduci.db import gsheets
from coviduci.db import sqlite
from absl import logging


class Synchronizer:
  """This will take data from the google sheet and put it into the sqlite DB.

  If the ICU name is already present, or the user telephone is already present,
  then it will *not* get updated.  If there is no existing row then
  a new row with the ICU or user info will get added."""

  def __init__(self, sheets_db, sqlite_db):
    self._shdb = sheets_db
    self._sqldb = sqlite_db

  def sync_hospitales(self):
    hospitales = self._shdb.get_data('Hospitales')
    self._sqldb.execute("DELETE FROM hospitales")
    for row in hospitales.iterrows():
      hospital = row[1]
      try:
        self._sqldb.upsert_hospitales(
          hospital["hospital"],
          hospital["c_uci"],
          hospital["c_usadas"],
          hospital["c_insatis"],
          hospital["medicos"],
          hospital["medicos_4"],
          hospital["medicos_c"],
          hospital["enfermeros"],
          hospital["enfermeros_4"],
          hospital["enfermeros_c"],
          hospital["auxiliares"],
          hospital["auxiliares_4"],
          hospital["auxiliares_c"],
          hospital["ter_resp"],
          hospital["ter_resp_4"],
          hospital["ter_resp_c"],
          hospital["p_ingresos"],
          hospital["p_alta"],
          hospital["p_fallecidos"],
          hospital["timestamp"],
        )
        logging.info("Agregamos hospital {}".format(hospital["hospital"]))
      except ValueError as e:
        logging.error(e)
        continue

  def sync_insumos(self):
    insumos = self._shdb.get_data('Insumos')
    self._sqldb.execute("DELETE FROM insumos")
    for row in insumos.iterrows():
      entry = row[1]
      try:
        self._sqldb.upsert_insumos(
          entry["hospital"],
          entry["n_a"],
          entry["adecuados"],
          entry["medios"],
          entry["criticos"],
          entry["nodisp"],
          entry["timestamp"],
        )
        logging.info("Agregamos insumos a {}".format(entry["hospital"]))
      except ValueError as e:
        logging.error(e)
        continue

  def sync_medicaciones(self):
    medicaciones = self._shdb.get_data('Medicaciones')
    self._sqldb.execute("DELETE FROM medicaciones")
    for row in medicaciones.iterrows():
      entry = row[1]
      try:
        self._sqldb.upsert_medicaciones(
          entry["hospital"],
          entry["n_a"],
          entry["adecuados"],
          entry["medios"],
          entry["criticos"],
          entry["nodisp"],
          entry["timestamp"],
        )
        logging.info("Agregamos medicaciones a {}".format(entry["hospital"]))
      except ValueError as e:
        logging.error(e)
        continue

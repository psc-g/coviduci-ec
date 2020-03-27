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
        )
        logging.info("Agregamos hospital {}".format(hospital["hospital"]))
      except ValueError as e:
        logging.error(e)
        continue

  def sync_camas(self):
    camas = self._shdb.get_data('Camas')
    self._sqldb.execute("DELETE FROM camas")
    for row in camas.iterrows():
      entry = row[1]
      try:
        self._sqldb.upsert_camas(
          entry["hospital"],
          entry["camas_total"],
          entry["camas_usadas"],
          entry["timestamp"],
        )
        logging.info("Agregamos camas a {}".format(entry["hospital"]))
      except ValueError as e:
        logging.error(e)
        continue

  def sync_personal(self):
    personal = self._shdb.get_data('Personal')
    self._sqldb.execute("DELETE FROM personal")
    for row in personal.iterrows():
      entry = row[1]
      try:
        self._sqldb.upsert_personal(
          entry["hospital"],
          entry["medicos"],
          entry["enfermeros"],
          entry["auxiliares"],
          entry["timestamp"],
        )
        logging.info("Agregamos personal a {}".format(entry["hospital"]))
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
          entry["respiradores"],
          entry["tubos_ett"],
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
          entry["primera"],
          entry["segunda"],
          entry["timestamp"],
        )
        logging.info("Agregamos medicaciones a {}".format(entry["hospital"]))
      except ValueError as e:
        logging.error(e)
        continue

  def sync_pacientes(self):
    pacientes = self._shdb.get_data('Pacientes')
    self._sqldb.execute("DELETE FROM pacientes")
    for row in pacientes.iterrows():
      entry = row[1]
      try:
        self._sqldb.upsert_pacientes(
          entry["hospital"],
          entry["ingresos"],
          entry["fallecidos"],
          entry["timestamp"],
        )
        logging.info("Agregamos pacientes a {}".format(entry["hospital"]))
      except ValueError as e:
        logging.error(e)
        continue

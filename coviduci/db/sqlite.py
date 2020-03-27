"""SQLite storage backend wrapper."""
from absl import logging
import os
import sqlite3
import time
import pandas as pd


class SQLiteDB:
  """Wraps SQLite DB for bed counts."""

  def __init__(self, db_path: str):
    """Given a token file and a sheet id, loads the sheet to be queried."""
    self._db_path = db_path

    if os.path.exists(db_path):
      self._conn = sqlite3.connect(db_path)
    else:
      self._conn = sqlite3.connect(db_path)
      self._create_table()

  def _create_table(self):
    self._conn.execute(
      """CREATE TABLE hospitales 
                                (id INTEGER NOT NULL PRIMARY KEY,
                                 hospital TEXT UNIQUE)"""
    )
    self._conn.execute(
      """CREATE TABLE camas
                           (hospital TEXT, camas_total INTEGER,
                            camas_usadas INTEGER, timestamp INTEGER)"""
    )
    self._conn.execute(
      """CREATE TABLE personal
                              (hospital TEXT, medicos INTEGER,
                               enfermeros INTEGER, auxiliares INTEGER, timestamp INTEGER)"""
    )
    self._conn.execute(
      """CREATE TABLE insumos
                             (hospital TEXT, respiradores INTEGER,
                              tubos_ett INTEGER, timestamp INTEGER)"""
    )
    self._conn.execute(
      """CREATE TABLE medicaciones
                                  (hospital TEXT, primera INTEGER,
                                   segunda INTEGER, tercera INTEGER, timestamp INTEGER)"""
    )
    self._conn.execute(
      """CREATE TABLE pacientes (hospital TEXT, ingresos INTEGER, fallecidos INTEGER, timestamp INTEGER)"""
    )
    self._conn.commit()

  def upsert_hospitales(
    self,
    hospital: str,
  ):
    """Add or update a hospital."""

    # If not then add:
    query = """INSERT INTO hospitales (hospital) VALUES ('{hospital}')"""
    self._conn.execute(query.format(**locals()))
    self._conn.commit()

  def upsert_camas(
    self,
    hospital: str,
    camas_total: int,
    camas_usadas: int,
    timestamp: int,
  ):
    """Add or update camas."""

    # If not then add:
    query = """INSERT INTO camas (hospital, camas_total, camas_usadas, timestamp)
                           VALUES
			   ('{hospital}', {camas_total}, {camas_usadas}, {timestamp})"""
    self._conn.execute(query.format(**locals()))
    self._conn.commit()

  def upsert_personal(
    self,
    hospital: str,
    medicos: int,
    enfermeros: int,
    auxiliares: int,
    timestamp: int,
  ):
    """Add or update personal."""

    # If not then add:
    query = """INSERT INTO personal (hospital, medicos, enfermeros, auxiliares, timestamp)
                           VALUES
			   ('{hospital}', {medicos}, {enfermeros}, {auxiliares}, {timestamp})"""
    self._conn.execute(query.format(**locals()))
    self._conn.commit()

  def upsert_insumos(
    self,
    hospital: str,
    respiradores: int,
    tubos_ett: int,
    timestamp: int,
  ):
    """Add or update insumos."""

    # If not then add:
    query = """INSERT INTO insumos (hospital, respiradores, tubos_ett, timestamp)
                           VALUES
			   ('{hospital}', {respiradores}, {tubos_ett}, {timestamp})"""
    self._conn.execute(query.format(**locals()))
    self._conn.commit()

  def upsert_medicaciones(
    self,
    hospital: str,
    primera: int,
    segunda: int,
    timestamp: int,
  ):
    """Add or update medicaciones."""

    # If not then add:
    query = """INSERT INTO medicaciones (hospital, primera, segunda, timestamp)
                           VALUES
			   ('{hospital}', {primera}, {segunda}, {timestamp})"""
    self._conn.execute(query.format(**locals()))
    self._conn.commit()

  def upsert_pacientes(
    self,
    hospital: str,
    ingresos: int,
    fallecidos: int,
    timestamp: int,
  ):
    """Add or update pacientes."""

    # If not then add:
    query = """INSERT INTO pacientes (hospital, ingresos, fallecidos, timestamp)
                           VALUES
			   ('{hospital}', {ingresos}, {fallecidos}, {timestamp})"""
    self._conn.execute(query.format(**locals()))
    self._conn.commit()

  def update_data(self, data):
    hospital = data['hospital']
    query = """SELECT count(hospital) as n_hospital FROM hospitales
               WHERE hospital = '{}'"""
    res = pd.read_sql_query(query.format(hospital), self._conn)
    if res.iloc[0]['n_hospital'] == 0:
      raise ValueError(f"Hospital {hospital} does not exist.")

    ts = int(time.time())
    table_modified = False
    # Camas update
    query = """SELECT camas_total, camas_usadas FROM camas WHERE hospital = '{}'"""
    res = pd.read_sql_query(query.format(hospital), self._conn)
    if (res.iloc[0]['camas_total'] != data['camas_total'] or
        res.iloc[0]['camas_usadas'] != data['camas_usadas']):
      query = """INSERT INTO camas (camas_total, camas_usadas, timestamp) VALUES ({}, {}, {})"""
      self._conn.execute(query.format(data['camas_total'], data['camas_usadas'], ts))
      table_modified = True
    # Personal update
    query = """SELECT medicos, enfermeros, auxiliares FROM personal WHERE hospital = '{}'"""
    res = pd.read_sql_query(query.format(hospital), self._conn)
    if (res.iloc[0]['medicos'] != data['medicos'] or
        res.iloc[0]['enfermeros'] != data['enfermeros'] or
        res.iloc[0]['auxiliares'] != data['auxiliares']):
      query = """INSERT INTO personal (medicos, enfermeros, auxiliares, timestamp) VALUES ({}, {}, {})"""
      self._conn.execute(query.format(data['medicos'], data['enfermeros'], data['auxiliares'], ts))
      table_modified = True
    # Insumos update
    query = """SELECT respiradores, tubos_ett FROM insumos WHERE hospital = '{}'"""
    res = pd.read_sql_query(query.format(hospital), self._conn)
    if (res.iloc[0]['respiradores'] != data['respiradores'] or
        res.iloc[0]['tubos_ett'] != data['tubos_ett']):
      query = """INSERT INTO insumos (respiradores, tubos_ett, timestamp) VALUES ({}, {}, {})"""
      self._conn.execute(query.format(data['respiradores'], data['tubos_ett'], ts))
      table_modified = True
    # Medicaciones update
    query = """SELECT primera, segunda FROM medicaciones WHERE hospital = '{}'"""
    res = pd.read_sql_query(query.format(hospital), self._conn)
    if (res.iloc[0]['primera'] != data['primera'] or
        res.iloc[0]['segunda'] != data['segunda']):
      query = """INSERT INTO medicaciones (primera, segunda, timestamp) VALUES ({}, {}, {})"""
      self._conn.execute(query.format(data['primera'], data['segunda'], ts))
      table_modified = True
    # Pacientes update
    query = """SELECT ingresos, fallecidos FROM pacientes WHERE hospital = '{}'"""
    res = pd.read_sql_query(query.format(hospital), self._conn)
    if (res.iloc[0]['ingresos'] != data['ingresos'] or
        res.iloc[0]['fallecidos'] != data['fallecidos']):
      query = """INSERT INTO pacientes (ingresos, fallecidos, timestamp) VALUES ({}, {}, {})"""
      self._conn.execute(query.format(data['ingresos'], data['fallecidos'], ts))
      table_modified = True
    if table_modified:
      self._conn.commit()

  def get_data(self, table):
    """Returns a pandas DF of data."""
    return pd.read_sql_query("""SELECT * FROM {}""".format(table), self._conn)

  def pd_execute(self, query):
    """Run pd.read_sql_query on a query and return the DataFrame."""
    return pd.read_sql_query(query, self._conn)

  def execute(self, query):
    self._conn.execute(query)
    self._conn.commit()

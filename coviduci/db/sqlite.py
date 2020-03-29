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
      logging.info('db_path: {}'.format(db_path))
      self._conn = sqlite3.connect(db_path)
      self._create_tables()

  def _create_tables(self):
    self._conn.execute(
      """CREATE TABLE hospitales 
                                (hospital TEXT NOT NULL,
                                 c_uci INTEGER,
                                 c_usadas INTEGER,
                                 c_insatis INTEGER,
                                 medicos INTEGER,
                                 medicos_4 INTEGER,
                                 medicos_c INTEGER,
                                 enfermeros INTEGER,
                                 enfermeros_4 INTEGER,
                                 enfermeros_c INTEGER,
                                 auxiliares INTEGER,
                                 auxiliares_4 INTEGER,
                                 auxiliares_c INTEGER,
                                 ter_resp INTEGER,
                                 ter_resp_4 INTEGER,
                                 ter_resp_c INTEGER,
                                 p_ingresos INTEGER,
                                 p_alta INTEGER,
                                 p_fallecidos INTEGER,
                                 timestamp INTEGER)"""
    )
    self._conn.execute(
      """CREATE TABLE insumos
                             (hospital TEXT, n_a TEXT, adecuados TEXT,
                              medios TEXT, criticos TEXT, nodisp TEXT,
                              timestamp INTEGER)"""
    )
    self._conn.execute(
      """CREATE TABLE medicaciones
                                  (hospital TEXT, n_a TEXT, adecuados TEXT,
                                   medios TEXT, criticos TEXT, nodisp TEXT,
                                   timestamp INTEGER)"""
    )
    self._conn.commit()

  def upsert_hospitales(
    self,
    hospital: str,
    c_uci: int,
    c_usadas: int,
    c_insatis: int,
    medicos: int,
    medicos_4: int,
    medicos_c: int,
    enfermeros: int,
    enfermeros_4: int,
    enfermeros_c: int,
    auxiliares: int,
    auxiliares_4: int,
    auxiliares_c: int,
    ter_resp: int,
    ter_resp_4: int,
    ter_resp_c: int,
    p_ingresos: int,
    p_alta: int,
    p_fallecidos: int,
    timestamp: int,
  ):
    """Add or update a hospital."""

    # If not then add:
    query = """INSERT INTO hospitales (hospital, c_uci, c_usadas, c_insatis,
                                       medicos, medicos_4, medicos_c,
                                       enfermeros, enfermeros_4, enfermeros_c,
                                       auxiliares, auxiliares_4, auxiliares_c,
                                       ter_resp, ter_resp_4, ter_resp_c,
                                       p_ingresos, p_alta, p_fallecidos,
                                       timestamp)
                                       VALUES
                                      ('{hospital}', {c_uci}, {c_usadas}, {c_insatis},
                                       {medicos}, {medicos_4}, {medicos_c},
                                       {enfermeros}, {enfermeros_4}, {enfermeros_c},
                                       {auxiliares}, {auxiliares_4}, {auxiliares_c},
                                       {ter_resp}, {ter_resp_4}, {ter_resp_c},
                                       {p_ingresos}, {p_alta}, {p_fallecidos}, {timestamp})"""
    self._conn.execute(query.format(**locals()))
    self._conn.commit()

  def upsert_insumos(
    self,
    hospital: str,
    n_a: str,
    adecuados: str,
    medios: str,
    criticos: str,
    nodisp: str,
    timestamp: int,
  ):
    """Add or update insumos."""

    # If not then add:
    query = """INSERT INTO insumos (hospital, n_a, adecuados, medios, criticos,
                                    nodisp, timestamp)
                           VALUES
			   ('{hospital}', '{n_a}', '{adecuados}', '{medios}', '{criticos}',
          '{nodisp}',{timestamp})"""
    self._conn.execute(query.format(**locals()))
    self._conn.commit()

  def upsert_medicaciones(
    self,
    hospital: str,
    n_a: str,
    adecuados: str,
    medios: str,
    criticos: str,
    nodisp: str,
    timestamp: int,
  ):
    """Add or update medicaciones."""

    # If not then add:
    query = """INSERT INTO medicaciones (hospital, n_a, adecuados, medios,
                                         criticos, nodisp, timestamp)
                           VALUES
			   ('{hospital}', '{n_a}', '{adecuados}', '{medios}', '{criticos}',
          '{nodisp}', {timestamp})"""
    self._conn.execute(query.format(**locals()))
    self._conn.commit()

  def update_data(self, **kwargs):
    query = """SELECT count(hospital) as n_hospital FROM hospitales
               WHERE hospital = '{hospital}'"""
    res = pd.read_sql_query(query.format(**kwargs), self._conn)
    if res.iloc[0]['n_hospital'] == 0:
      raise ValueError(f"Hospital {hospital} does not exist.")

    ts = int(time.time())
    # Hospitales update
    query = """INSERT INTO hospitales (hospital, c_uci, c_usadas, c_insatis,
                                       medicos, medicos_4, medicos_c,
                                       enfermeros, enfermeros_4, enfermeros_c,
                                       auxiliares, auxiliares_4, auxiliares_c,
                                       ter_resp, ter_resp_4, ter_resp_c,
                                       p_ingresos, p_alta,
                                       p_fallecidos, timestamp)
                                       VALUES
                                      ('{hospital}', {c_uci}, {c_usadas}, {c_insatis},
                                       {medicos}, {medicos_4}, {medicos_c},
                                       {enfermeros}, {enfermeros_4}, {enfermeros_c},
                                       {auxiliares}, {auxiliares_4}, {auxiliares_c},
                                       {ter_resp}, {ter_resp_4}, {ter_resp_c},
                                       {p_ingresos}, {p_alta}, {p_fallecidos},
                                       {timestamp})"""
    self._conn.execute(query.format(timestamp=ts, **kwargs))
    # Insumos update
    for insumo in ['respiradores', 'tubos_ett', 'mascarillas', 'prot_personal']:
      query = """INSERT INTO insumos (hospital, {status}, timestamp)
                 VALUES ('{hospital}', '{insumo}', {timestamp})"""
      self._conn.execute(query.format(status=kwargs[insumo], insumo=insumo,
                         timestamp=ts, **kwargs))
    # Medicaciones update
    for medicacion in ['midazolam', 'propofol', 'dexmedetomidina', 'fentanilo',
                       'rocuronio', 'norepinefrina', 'dopamina', 'dobutamina',
                       'antivirales', 'azitromicina', 'ceftriaxone',
                       'ampicilina_sulbactam', 'piperazilina', 'enoxaheparina',
                       'metilprednisolona', 'dexametasona']:
      query = """INSERT INTO medicaciones (hospital, {status}, timestamp)
                 VALUES ('{hospital}', '{medicacion}', {timestamp})"""
      self._conn.execute(query.format(status=kwargs[medicacion],
                                      medicacion=medicacion, timestamp=ts,
                                      **kwargs))
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

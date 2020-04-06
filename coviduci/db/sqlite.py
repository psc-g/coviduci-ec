"""SQLite storage backend wrapper."""
from absl import logging
import getpass
import os
import sqlite3
import time
import tornado.escape
import pandas as pd


def unescape_html(s):
  """Unescapes an HTML-escaped string, returns username and display name."""
  replacements = [
      ('+', (' ', '_')),
      ('%C3%81', ('Á', 'A')),
      ('%C3%A1', ('á', 'a')),
      ('%C3%89', ('É', 'E')),
      ('%C3%A9', ('é', 'e')),
      ('%C3%8D', ('Í', 'I')),
      ('%C3%AD', ('í', 'i')),
      ('%C3%93', ('Ó', 'O')),
      ('%C3%B3', ('ó', 'o')),
      ('%C3%9A', ('Ú', 'U')),
      ('%C3%BA', ('ú', 'u')),
      ('%C3%84', ('Ä', 'A')),
      ('%C3%A4', ('ä', 'a')),
      ('%C3%8B', ('Ë', 'E')),
      ('%C3%AB', ('ë', 'e')),
      ('%C3%8F', ('Ï', 'I')),
      ('%C3%AF', ('ï', 'i')),
      ('%C3%96', ('Ö', 'O')),
      ('%C3%B6', ('ö', 'o')),
      ('%C3%9C', ('Ü', 'U')),
      ('%C3%BC', ('ü', 'u')),
  ]
  display_name = s
  hospital = s
  for r in replacements:
    display_name = display_name.replace(r[0], r[1][0])
    hospital = hospital.replace(r[0], r[1][1])
  hospital = hospital.lower()
  return hospital, display_name


class SQLiteDB:
  """Wraps SQLite DB for bed counts."""

  def __init__(self, db_path, token_encoder):
    """Construct the SQLite object."""
    self._db_path = db_path
    self.token_encoder = token_encoder

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
                                 timestamp INTEGER,
                                 c_usadas_otras INTEGER,
                                 p_ingresos_otros INTEGER,
                                 p_ingresos_sosp INTEGER,
                                 p_alta_otros INTEGER,
                                 p_fallecidos_otros INTEGER,
                                 p_fallecidos_sosp INTEGER)"""
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

  def create_users(self):
    """Create the users table, initially only with the admin logins."""
    self._conn.execute(
        """CREATE TABLE users
           (name TEXT PRIMARY KEY NOT NULL, login TEXT NOT NULL,
            display_name TEXT NOT NULL)""")
    display_name = input('Enter a name for the admin account: ')
    pwd = getpass.getpass(prompt='Enter a password for the admin account: ')
    pwd = self.token_encoder.encode(pwd)
    add_user = """INSERT INTO users (name, login, display_name) VALUES
                  ('{name}', '{pwd}', '{display_name}')"""
    self._conn.execute(add_user.format(name='admin', pwd=pwd,
                                       display_name=display_name))
    display_name = input('Enter a name for the ministry: ')
    pwd = getpass.getpass(prompt='Enter a password for the ministry: ')
    pwd = self.token_encoder.encode(pwd)
    self._conn.execute(add_user.format(name='ministerio', pwd=pwd,
                                       display_name=display_name))
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
    c_usadas_otras: int,
    p_ingresos_otros: int,
    p_ingresos_sosp: int,
    p_alta_otros: int,
    p_fallecidos_otros: int,
    p_fallecidos_sosp: int,
  ):
    """Add or update a hospital."""

    # If not then add:
    query = """INSERT INTO hospitales (hospital, c_uci, c_usadas,
                                       c_usadas_otras, c_insatis,
                                       medicos, medicos_4, medicos_c,
                                       enfermeros, enfermeros_4, enfermeros_c,
                                       auxiliares, auxiliares_4, auxiliares_c,
                                       ter_resp, ter_resp_4, ter_resp_c,
                                       p_ingresos, p_alta, p_fallecidos,
                                       p_ingresos_otros, p_ingresos_sosp,
                                       p_alta_otros, p_fallecidos_otros,
                                       p_fallecidos_sosp, timestamp)
                                       VALUES
                                      ('{hospital}', {c_uci}, {c_usadas},
                                        {c_usadas_otras}, {c_insatis},
                                        {medicos}, {medicos_4}, {medicos_c},
                                        {enfermeros}, {enfermeros_4}, {enfermeros_c},
                                        {auxiliares}, {auxiliares_4}, {auxiliares_c},
                                        {ter_resp}, {ter_resp_4}, {ter_resp_c},
                                        {p_ingresos}, {p_alta}, {p_fallecidos},
                                        {p_ingresos_otros}, {p_ingresos_sosp},
                                        {p_alta_otros}, {p_fallecidos_otros},
                                        {p_fallecidos_sosp}, {timestamp})"""
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
    if 'user' not in kwargs:
      logging.info('ERROR: "user" not in kwargs')
      return
    if kwargs['user'] == 'admin':
      if 'display_name' not in kwargs or 'clave' not in kwargs:
        logging.info('ERROR: "display_name" or "clave" not in kwargs')
        return
      hospital, display_name = unescape_html(kwargs['display_name'])
      add_user = """INSERT INTO users (name, login, display_name) VALUES
                                      ('{hospital}', '{clave}',
                                       '{display_name}')"""
      self._conn.execute(add_user.format(
          hospital=hospital, clave=self.token_encoder.encode(kwargs['clave']),
          display_name=display_name))
      kwargs['hospital'] = hospital
    else:
      query = """SELECT count(hospital) as n_hospital FROM hospitales
                 WHERE hospital = '{hospital}'"""
      res = pd.read_sql_query(query.format(**kwargs), self._conn)
      if res.iloc[0]['n_hospital'] == 0:
        raise ValueError(f"Hospital {hospital} does not exist.")

    ts = int(time.time())
    # Hospitales update
    query = """INSERT INTO hospitales (hospital, c_uci, c_usadas,
                                       c_usadas_otras, c_insatis,
                                       medicos, medicos_4, medicos_c,
                                       enfermeros, enfermeros_4, enfermeros_c,
                                       auxiliares, auxiliares_4, auxiliares_c,
                                       ter_resp, ter_resp_4, ter_resp_c,
                                       p_ingresos, p_alta, p_fallecidos,
                                       p_ingresos_otros, p_ingresos_sosp,
                                       p_alta_otros, p_fallecidos_otros,
                                       p_fallecidos_sosp, timestamp)
                                       VALUES
                                      ('{hospital}', {c_uci}, {c_usadas},
                                        {c_usadas_otras}, {c_insatis},
                                        {medicos}, {medicos_4}, {medicos_c},
                                        {enfermeros}, {enfermeros_4}, {enfermeros_c},
                                        {auxiliares}, {auxiliares_4}, {auxiliares_c},
                                        {ter_resp}, {ter_resp_4}, {ter_resp_c},
                                        {p_ingresos}, {p_alta}, {p_fallecidos},
                                        {p_ingresos_otros}, {p_ingresos_sosp},
                                        {p_alta_otros}, {p_fallecidos_otros},
                                        {p_fallecidos_sosp}, {timestamp})"""
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

  def check_login(self, user, encoded_login):
    res = pd.read_sql_query(
        """SELECT * FROM users WHERE name = '{user}' AND login = '{encoded_login}'""".format(
            user=user, encoded_login=encoded_login),
        self._conn)
    if res.empty:
      return None
    else:
      return res.iloc[0]['name']

  def update_login(self, original_login, new_login):
    query = """UPDATE users SET login = '{new_login}'
               WHERE login = '{original_login}'"""
    try:
      self._conn.execute(query.format(new_login=new_login,
                                      original_login=original_login))
      self._conn.commit()
      return True
    except:
      return False

  def get_display_name(self, user):
    res = pd.read_sql_query(
        """SELECT * FROM users WHERE name = '{}'""".format(user), self._conn)
    if res.empty:
      return None
    else:
      return res.iloc[0]['display_name']

  def get_hospitals(self):
    res = pd.read_sql_query('SELECT display_name FROM users', self._conn)
    return res['display_name'].to_list()

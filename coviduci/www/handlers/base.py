from absl import logging
import math
import numpy as np
import pandas as pd
import time
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
  """A base class for handlers."""

  TABLES = ['insumos', 'medicaciones']
  DEFAULT_VALUES = {
      'c_uci': 0,
      'c_usadas': 0,
      'c_insatis': 0,
      'medicos': 0,
      'medicos_4': 0,
      'medicos_c': 0,
      'enfermeros': 0,
      'enfermeros_4': 0,
      'enfermeros_c': 0,
      'auxiliares': 0,
      'auxiliares_4': 0,
      'auxiliares_c': 0,
      'ter_resp': 0,
      'ter_resp_4': 0,
      'ter_resp_c': 0,
      'p_ingresos': 0,
      'p_alta': 0,
      'p_fallecidos': 0,
  }
  REQUIRED_FIELDS = {
      'insumos': ['respiradores', 'tubos_ett', 'prot_personal', 'mascarillas'],
      'medicaciones': ['midazolam',
                       'propofol',
                       'dexmedetomidina',
                       'fentanilo',
                       'rocuronio',
                       'norepinefrina',
                       'dopamina',
                       'dobutamina',
                       'antivirales',
                       'azitromicina',
                       'ceftriaxone',
                       'ampicilina_sulbactam',
                       'piperazilina',
                       'enoxaheparina',
                       'metilprednisolona',
                       'dexametasona',
                       'hidroxicloroquina'],
  }
  REQUIRED_CATEGORIES = ['n_a', 'adecuados', 'medios', 'criticos', 'nodisp']
  COOKIE = 'id'

  def _time_ago(self, ts) -> str:
    if ts is None:
      return 'jamás'
  
    delta = int(time.time() - int(ts))
    units = [(86400, 'día'), (3600, 'hora'), (60, 'minuto'), (1, 'segundo')]
    for unit, name in sorted(units, reverse=True):
      curr = delta // unit
      if curr > 0:
        plural = '' if curr == 1 else 's' # hack
        return 'hace {} {}{}'.format(curr, name, plural)
    return 'ahorita'

  def _get_data(self, hospital, aggregated):
    df = self.db.get_data('hospitales')
    df = df[df.hospital == hospital]
    if df.empty:
      return None
    df = df[df.timestamp == max(df.timestamp)]
    last_updates = {'hospitales': int(df.timestamp)}
    data = {
        'hospital': hospital,
        'c_uci': int(max(df.c_uci)),
        'c_usadas': int(max(df.c_usadas)),
        'c_insatis': int(max(df.c_insatis)),
        'medicos': int(max(df.medicos)),
        'medicos_4': int(max(df.medicos_4)),
        'medicos_c': int(max(df.medicos_4)),
        'enfermeros': int(max(df.enfermeros)),
        'enfermeros_4': int(max(df.enfermeros_4)),
        'enfermeros_c': int(max(df.enfermeros_4)),
        'auxiliares': int(max(df.auxiliares)),
        'auxiliares_4': int(max(df.auxiliares_4)),
        'auxiliares_c': int(max(df.auxiliares_4)),
        'ter_resp': int(max(df.ter_resp)),
        'ter_resp_4': int(max(df.ter_resp_4)),
        'ter_resp_c': int(max(df.ter_resp_4)),
        'p_ingresos': int(max(df.p_ingresos)),
        'p_alta': int(max(df.p_alta)),
        'p_fallecidos': int(max(df.p_fallecidos)),
    }
    required = {t: None for t in self.TABLES}
    if aggregated:
      for cat in self.REQUIRED_CATEGORIES:
        data[cat] = []
    for table in self.TABLES:
      table_df = self.db.get_data(table)
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
          if aggregated:
            data[category].append(field)
          else:
            data[field] = category
        else:
          if aggregated:
            data['n_a'].append(field)
          else:
            data[field] = 'n_a'
      last_updates[table] = max(table_df.timestamp)
    data['last_update'] = self._time_ago(max(list(last_updates.values())))
    return data

  def get_template_path(self):
    return 'coviduci/www/templates/'

  def get_current_user(self):
    return self.get_secure_cookie(self.COOKIE)

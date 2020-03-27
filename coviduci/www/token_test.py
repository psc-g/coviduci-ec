import unittest
from coviduci.www import token
from coviduci import config


class TokenTest(unittest.TestCase):

  def test_encode(self):
    cfg = config.Config('resources/test.toml')
    tkn = token.TokenEncoder(cfg)
    userid = 1234
    encoded = tkn.encode(userid)
    self.assertIsInstance(encoded, str)
    self.assertEqual(tkn.decode(encoded), userid)

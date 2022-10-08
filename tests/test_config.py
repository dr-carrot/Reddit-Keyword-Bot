import os
import sys
import unittest

import yaml

from src.app import config
from unittest.mock import MagicMock, patch


class TestUtilityMethods(unittest.TestCase):

    def test_to_env_var(self):
        res = config.to_env_var('abc', var_path='def')
        self.assertEqual('BOT_ABC_DEF', res)

    def test_to_env_var_none(self):
        res = config.to_env_var('abc')
        self.assertEqual('BOT_ABC', res)

    def test_flatten(self):
        test_dict = {
            'abd': {
                'def': {
                    'ghi': 'hij'
                }
            }
        }
        res = config.flatten(test_dict)
        self.assertEqual({'abd_def_ghi': 'hij'}, res)

    def test_flatten_string(self):
        res = config.flatten('hello')
        self.assertEqual('hello', res)

    def test_apply_value_to_dict_path(self):
        test_dict = {
            'abc': {
                'def': {
                    'ghi': 'jlk'
                }
            }
        }
        config.apply_value_to_dict_path(test_dict, ['abc', 'def', 'ghi'], 'cat')
        self.assertEqual('cat', test_dict['abc']['def']['ghi'])

    def test_apply_value_to_dict_path_new_val(self):
        test_dict = {
            'abc': {
                'def': {
                    'ghi': 'jlk'
                }
            }
        }
        config.apply_value_to_dict_path(test_dict, ['xyz', 'def', 'xyz'], 'cat')
        self.assertEqual('cat', test_dict['xyz']['def']['xyz'])

    def test_merge(self):
        test_dict1 = {
            'abc': {
                'def': {
                    'ghi': 'jlk',
                    'mno': 'pqr'
                }
            }
        }
        test_dict2 = {
            'abc': {
                'def': {
                    'ghi': 'duck',
                    'mno': 'pqr',
                    'xyz': 'cat'
                }
            }
        }
        res = config.merge(test_dict1, test_dict2)
        self.assertEqual('duck', res['abc']['def']['ghi'])
        self.assertEqual('cat', res['abc']['def']['xyz'])
        self.assertEqual('pqr', res['abc']['def']['mno'])

    def test_safe_config(self):
        config.configuration = config.BotProperties()
        res = config.safe_config()
        self.assertNotEqual(config.configuration.__dict__, res)


class TestInitialize(unittest.TestCase):
    def setUp(self) -> None:
        self.reset_env_vars()

    def tearDown(self) -> None:
        self.reset_env_vars()

    def reset_env_vars(self):
        for v in filter(lambda x: x.startswith('BOT_'), os.environ.keys()):
            if v in os.environ:
                del os.environ[v]

    def get_config(self, config_path='../examples/sample.yaml'):
        os.environ['BOT_CONFIG_PATH'] = config_path
        with open(config_path) as f:
            data = yaml.safe_load(f)
            return data

    def test_initialize_load_yaml(self):
        self.get_config()
        res = config.initialize()
        print(list(filter(lambda x: x.startswith('BOT_'), os.environ.keys())))
        self.assertTrue(res)

    @patch('os.path.exists', MagicMock(return_value=False))
    def test_initialize_load_yaml_fail(self):
        res = config.initialize()
        self.assertFalse(res)

    def test_initialize_load_env_missing_vars(self):
        cfg = self.get_config()
        cfg['scraper'] = None
        os.environ['BOT_SCRAPERJSON'] = '[{}]'
        with patch('yaml.safe_load', MagicMock(return_value=cfg)):
            res = config.initialize()
        self.assertFalse(res)


if __name__ == '__main__':
    unittest.main()

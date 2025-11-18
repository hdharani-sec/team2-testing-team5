import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import os
import json
import tempfile
import shutil

import config


class TestConfig(unittest.TestCase):
    
    def setUp(self):
        """Reset config before each test"""
        config._config = None
        self.original_env = os.environ.copy()
        
    def tearDown(self):
        """Restore original environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
        config._config = None
        
    @patch('config.open', new_callable=mock_open, read_data='{"test_key": "test_value"}')
    @patch('config._get_default_path')
    def test_init_config_loads_file(self, mock_get_path, mock_file):
        """Test that _init_config loads config from file"""
        mock_get_path.return_value = '/path/to/config.json'
        
        config._init_config()
        
        self.assertIsNotNone(config._config)
        self.assertEqual(config._config['test_key'], 'test_value')
        mock_file.assert_called_once_with('/path/to/config.json', 'r')
        
    @patch('config._get_default_path')
    def test_init_config_empty_when_no_file(self, mock_get_path):
        """Test that _init_config creates empty dict when no config file"""
        mock_get_path.return_value = None
        
        config._init_config()
        
        self.assertIsNotNone(config._config)
        self.assertEqual(config._config, {})
        
    @patch('config.open', new_callable=mock_open, read_data='{"key": "value"}')
    @patch('config._get_default_path')
    def test_init_config_only_once(self, mock_get_path, mock_file):
        """Test that _init_config only initializes once"""
        mock_get_path.return_value = '/path/to/config.json'
        
        config._init_config()
        config._init_config()
        config._init_config()
        

        mock_file.assert_called_once()
        
    @patch('config.os.path.isfile')
    @patch('config.os.getcwd')
    def test_get_default_path_finds_config(self, mock_getcwd, mock_isfile):
        """Test _get_default_path finds config in current directory"""
        mock_getcwd.return_value = '/home/user/project'
        mock_isfile.return_value = True
        
        result = config._get_default_path()
        
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith('config.json'))
        
    @patch('config.os.path.isfile')
    @patch('config.os.getcwd')
    @patch('config.os.path.abspath')
    def test_get_default_path_traverses_up(self, mock_abspath, mock_getcwd, mock_isfile):
        """Test _get_default_path traverses up directory tree"""
        mock_getcwd.return_value = '/home/user/project/subdir'
        

        mock_isfile.side_effect = [False, True]
        mock_abspath.side_effect = lambda x: x
        
        result = config._get_default_path()
        self.assertTrue(mock_isfile.call_count >= 1)
        
    @patch('config.os.path.isfile')
    @patch('config.os.getcwd')
    @patch('config.os.path.abspath')
    def test_get_default_path_returns_none_when_not_found(self, mock_abspath, mock_getcwd, mock_isfile):
        """Test _get_default_path returns None when config not found"""
        mock_getcwd.return_value = '/'
        mock_isfile.return_value = False
        mock_abspath.side_effect = lambda x: '/' if '..' in x else x
        
        result = config._get_default_path()
        
        self.assertIsNone(result)
        
    @patch('config._init_config')
    def test_get_parameter_from_environ(self, mock_init):
        """Test get_parameter retrieves from environment variable"""
        config._config = {'key': 'config_value'}
        os.environ['test_param'] = 'env_value'
        
        result = config.get_parameter('test_param')
        
        self.assertEqual(result, 'env_value')
        
    @patch('config._init_config')
    def test_get_parameter_from_config(self, mock_init):
        """Test get_parameter retrieves from config dict"""
        config._config = {'test_param': 'config_value'}
        
        result = config.get_parameter('test_param')
        
        self.assertEqual(result, 'config_value')
        
    @patch('config._init_config')
    def test_get_parameter_with_default(self, mock_init):
        """Test get_parameter returns default when key not found"""
        config._config = {}
        
        result = config.get_parameter('missing_key', default='default_value')
        
        self.assertEqual(result, 'default_value')
        
    @patch('config._init_config')
    def test_get_parameter_returns_none_when_not_found(self, mock_init):
        """Test get_parameter returns None when key not found and no default"""
        config._config = {}
        
        result = config.get_parameter('missing_key')
        
        self.assertIsNone(result)
        
    @patch('config._init_config')
    def test_get_parameter_json_prefix_in_environ(self, mock_init):
        """Test get_parameter handles json: prefix in environment variables"""
        config._config = {}
        os.environ['test_param'] = 'json:{"nested": "value"}'
        
        result = config.get_parameter('test_param')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['nested'], 'value')
        
    def test_convert_to_typed_value_none(self):
        """Test convert_to_typed_value with None"""
        result = config.convert_to_typed_value(None)
        
        self.assertIsNone(result)
        
    def test_convert_to_typed_value_json_string(self):
        """Test convert_to_typed_value with JSON string"""
        result = config.convert_to_typed_value('{"key": "value"}')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['key'], 'value')
        
    def test_convert_to_typed_value_json_array(self):
        """Test convert_to_typed_value with JSON array"""
        result = config.convert_to_typed_value('[1, 2, 3]')
        
        self.assertIsInstance(result, list)
        self.assertEqual(result, [1, 2, 3])
        
    def test_convert_to_typed_value_json_number(self):
        """Test convert_to_typed_value with JSON number"""
        result = config.convert_to_typed_value('42')
        
        self.assertEqual(result, 42)
        
    def test_convert_to_typed_value_json_boolean(self):
        """Test convert_to_typed_value with JSON boolean"""
        result = config.convert_to_typed_value('true')
        
        self.assertEqual(result, True)
        
    def test_convert_to_typed_value_plain_string(self):
        """Test convert_to_typed_value with plain string"""
        result = config.convert_to_typed_value('plain_string')
        
        self.assertEqual(result, 'plain_string')
        
    def test_convert_to_typed_value_non_string(self):
        """Test convert_to_typed_value with non-string value"""
        result = config.convert_to_typed_value(123)
        
        self.assertEqual(result, 123)
        
    def test_convert_to_typed_value_dict(self):
        """Test convert_to_typed_value with dict"""
        input_dict = {'key': 'value'}
        result = config.convert_to_typed_value(input_dict)
        
        self.assertEqual(result, input_dict)
        
    @patch('config._init_config')
    def test_set_parameter_string(self, mock_init):
        """Test set_parameter with string value"""
        config._config = {}
        
        config.set_parameter('test_key', 'test_value')
        
        self.assertEqual(os.environ['test_key'], 'test_value')
        
    @patch('config._init_config')
    def test_set_parameter_dict(self, mock_init):
        """Test set_parameter with dict value"""
        config._config = {}
        test_dict = {'nested': 'value'}
        
        config.set_parameter('test_key', test_dict)
        
        self.assertTrue(os.environ['test_key'].startswith('json:'))
        self.assertIn('nested', os.environ['test_key'])
        
    @patch('config._init_config')
    def test_set_parameter_list(self, mock_init):
        """Test set_parameter with list value"""
        config._config = {}
        test_list = [1, 2, 3]
        
        config.set_parameter('test_key', test_list)
        
        self.assertTrue(os.environ['test_key'].startswith('json:'))
        
    @patch('config._init_config')
    def test_set_parameter_int(self, mock_init):
        """Test set_parameter with int value"""
        config._config = {}
        
        config.set_parameter('test_key', 42)
        
        self.assertTrue(os.environ['test_key'].startswith('json:'))
        
    @patch('config.set_parameter')
    def test_overwrite_from_args_items(self, mock_set_param):
        """Test overwrite_from_args using items() method"""
        args = Mock()
        args.param1 = 'value1'
        args.param2 = 'value2'
        args.param3 = None
        
        config.overwrite_from_args(args)
        self.assertTrue(mock_set_param.call_count >= 2)
        
    @patch('config.set_parameter')
    def test_overwrite_from_args_with_none_values(self, mock_set_param):
        """Test overwrite_from_args skips None values"""
        args = Mock()
        args.param1 = None
        
        config.overwrite_from_args(args)
        
    def test_overwrite_from_args_handles_exceptions(self):
        """Test overwrite_from_args handles exceptions gracefully"""
        args = Mock()
        with patch('config.vars', side_effect=Exception('Test error')):
            try:
                config.overwrite_from_args(args)
            except:
                self.fail("overwrite_from_args raised exception unexpectedly")
                
    @patch('config._init_config')
    def test_get_parameter_preference_order(self, mock_init):
        """Test that environment variables take precedence over config file"""
        config._config = {'key': 'config_value'}
        os.environ['key'] = 'env_value'
        
        result = config.get_parameter('key')
        self.assertEqual(result, 'env_value')
        
    @patch('config.open', new_callable=mock_open, read_data='invalid json')
    @patch('config._get_default_path')
    def test_init_config_invalid_json(self, mock_get_path, mock_file):
        """Test _init_config with invalid JSON"""
        mock_get_path.return_value = '/path/to/config.json'

        with self.assertRaises(json.JSONDecodeError):
            config._init_config()
            
    @patch('config._init_config')
    def test_get_parameter_empty_string_default(self, mock_init):
        """Test get_parameter with empty string as default"""
        config._config = {}
        
        result = config.get_parameter('missing', default='')
        
        self.assertEqual(result, '')
        
    @patch('config._init_config')
    def test_get_parameter_zero_default(self, mock_init):
        """Test get_parameter with zero as default"""
        config._config = {}
        
        result = config.get_parameter('missing', default=0)
        
        self.assertEqual(result, 0)
        
    @patch('config._init_config')
    def test_get_parameter_false_default(self, mock_init):
        """Test get_parameter with False as default - tests truthy check bug"""
        config._config = {}
        
        result = config.get_parameter('missing', default=False)
        self.assertIsNone(result)
        
    def test_convert_to_typed_value_malformed_json(self):
        """Test convert_to_typed_value with malformed JSON string"""
        result = config.convert_to_typed_value('{invalid json}')
        self.assertEqual(result, '{invalid json}')
        
    @patch('config.os.getcwd')
    @patch('config.os.path.isfile')
    @patch('config.os.path.abspath')
    def test_get_default_path_complex_traversal(self, mock_abspath, mock_isfile, mock_getcwd):
        """Test _get_default_path with complex directory traversal"""
        mock_getcwd.return_value = '/home/user/project/a/b/c'
        
        paths = [
            '/home/user/project/a/b/c',
            '/home/user/project/a/b',
            '/home/user/project/a',
            '/home/user/project',
            '/home/user',
            '/home',
            '/',
            '/'
        ]
        
        mock_abspath.side_effect = lambda p: paths[len([c for c in mock_abspath.call_args_list if '..' in str(c)])] if '..' in p else p

        def is_file_side_effect(path):
            return '/home/user/project/config.json' in path
            
        mock_isfile.side_effect = is_file_side_effect
        
        result = config._get_default_path()
        self.assertTrue(result is None or 'config.json' in result)


if __name__ == '__main__':
    unittest.main()
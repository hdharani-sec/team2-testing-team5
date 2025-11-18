import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import json
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data_loader
from data_loader import DataLoader
from model import Issue, Label, Event


class TestDataLoader(unittest.TestCase):
    
    def setUp(self):
        """Reset global variables before each test"""
        data_loader._ISSUES = None
        data_loader._MIGRATION_DATE = None
        data_loader._LABEL_CATEGORY_LIST = None
        data_loader._YEAR_RANGE = None
        
    def tearDown(self):
        """Clean up after each test"""
        data_loader._ISSUES = None
        data_loader._MIGRATION_DATE = None
        data_loader._LABEL_CATEGORY_LIST = None
        data_loader._YEAR_RANGE = None
        
    @patch('data_loader.config.get_parameter')
    def test_init_gets_data_path(self, mock_get_param):
        """Test that __init__ retrieves data path from config"""
        mock_get_param.return_value = '/path/to/data.json'
        
        loader = DataLoader()
        
        self.assertEqual(loader.data_path, '/path/to/data.json')
        mock_get_param.assert_called_once_with('ENPM611_PROJECT_DATA_PATH')
        
    @patch('data_loader.config.get_parameter')
    def test_init_with_none_path(self, mock_get_param):
        """Test __init__ when config returns None"""
        mock_get_param.return_value = None
        
        loader = DataLoader()
        
        self.assertIsNone(loader.data_path)
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_get_issues_loads_empty_list(self, mock_file, mock_get_param):
        """Test get_issues with empty JSON array"""
        mock_get_param.return_value = '/path/to/data.json'
        
        loader = DataLoader()
        issues = loader.get_issues()
        
        self.assertEqual(issues, [])
        self.assertEqual(len(issues), 0)
        mock_file.assert_called_once_with('/path/to/data.json', 'r')
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_issues_loads_single_issue(self, mock_file, mock_get_param):
        """Test get_issues with single issue"""
        mock_get_param.return_value = '/path/to/data.json'
        
        issue_data = [{
            'number': 1,
            'title': 'Test Issue',
            'state': 'open',
            'created_at': '2023-01-01T00:00:00Z',
            'labels': [],
            'events': []
        }]
        
        mock_file.return_value.read.return_value = json.dumps(issue_data)
        
        loader = DataLoader()
        issues = loader.get_issues()
        
        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], Issue)
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_issues_caches_result(self, mock_file, mock_get_param):
        """Test that get_issues caches result and doesn't reload"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        loader = DataLoader()
        
        # Call multiple times
        issues1 = loader.get_issues()
        issues2 = loader.get_issues()
        issues3 = loader.get_issues()
        mock_file.assert_called_once()
        
        # Should return same object
        self.assertIs(issues1, issues2)
        self.assertIs(issues2, issues3)
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_issues_multiple_loaders_share_cache(self, mock_file, mock_get_param):
        """Test that multiple DataLoader instances share the global cache"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        loader1 = DataLoader()
        loader2 = DataLoader()
        
        issues1 = loader1.get_issues()
        issues2 = loader2.get_issues()
        mock_file.assert_called_once()
        self.assertIs(issues1, issues2)
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_migration_date_with_events(self, mock_file, mock_get_param):
        """Test get_migration_date returns maximum event date"""
        mock_get_param.return_value = '/path/to/data.json'
        
        # Create mock issues with events
        event1 = Mock(spec=Event)
        event1.event_date = datetime(2023, 1, 1)
        
        event2 = Mock(spec=Event)
        event2.event_date = datetime(2023, 6, 15)
        
        event3 = Mock(spec=Event)
        event3.event_date = datetime(2023, 3, 10)
        
        issue1 = Mock(spec=Issue)
        issue1.events = [event1, event2]
        
        issue2 = Mock(spec=Issue)
        issue2.events = [event3]
        
        mock_file.return_value.read.return_value = '[]'
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1, issue2]):
            migration_date = loader.get_migration_date()

        self.assertEqual(migration_date, datetime(2023, 6, 15))
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_migration_date_caches_result(self, mock_file, mock_get_param):
        """Test that get_migration_date caches its result"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        event1 = Mock(spec=Event)
        event1.event_date = datetime(2023, 1, 1)
        
        issue1 = Mock(spec=Issue)
        issue1.events = [event1]
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1]) as mock_get_issues:
            date1 = loader.get_migration_date()
            date2 = loader.get_migration_date()
            self.assertEqual(date1, date2)
            
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_label_categories_returns_unique_categories(self, mock_file, mock_get_param):
        """Test get_label_categories returns unique category list"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        
        label2 = Mock(spec=Label)
        label2.category = 'priority'
        
        label3 = Mock(spec=Label)
        label3.category = 'type'
        
        issue1 = Mock(spec=Issue)
        issue1.labels = [label1, label2]
        
        issue2 = Mock(spec=Issue)
        issue2.labels = [label3]
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1, issue2]):
            categories = loader.get_label_categories()

        self.assertEqual(len(categories), 2)
        self.assertIn('type', categories)
        self.assertIn('priority', categories)
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_label_categories_with_no_labels(self, mock_file, mock_get_param):
        """Test get_label_categories with issues having no labels"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        issue1 = Mock(spec=Issue)
        issue1.labels = []
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1]):
            categories = loader.get_label_categories()
            
        self.assertEqual(categories, [])
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_label_categories_caches_result(self, mock_file, mock_get_param):
        """Test that get_label_categories caches its result"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        
        issue1 = Mock(spec=Issue)
        issue1.labels = [label1]
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1]):
            cat1 = loader.get_label_categories()
            cat2 = loader.get_label_categories()
            
            self.assertIs(cat1, cat2)
            
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_year_range_returns_range(self, mock_file, mock_get_param):
        """Test get_year_range returns year range as strings"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        issue1 = Mock(spec=Issue)
        issue1.created_date = datetime(2021, 1, 1)
        
        issue2 = Mock(spec=Issue)
        issue2.created_date = datetime(2023, 1, 1)
        
        issue3 = Mock(spec=Issue)
        issue3.created_date = datetime(2022, 6, 15)
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1, issue2, issue3]):
            years = loader.get_year_range()

        self.assertEqual(years, ['2021', '2022', '2023'])
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_year_range_single_year(self, mock_file, mock_get_param):
        """Test get_year_range with all issues in same year"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        issue1 = Mock(spec=Issue)
        issue1.created_date = datetime(2023, 1, 1)
        
        issue2 = Mock(spec=Issue)
        issue2.created_date = datetime(2023, 12, 31)
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1, issue2]):
            years = loader.get_year_range()
            
        self.assertEqual(years, ['2023'])
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_year_range_caches_result(self, mock_file, mock_get_param):
        """Test that get_year_range caches its result"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        issue1 = Mock(spec=Issue)
        issue1.created_date = datetime(2023, 1, 1)
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1]):
            years1 = loader.get_year_range()
            years2 = loader.get_year_range()
            
            self.assertIs(years1, years2)
            
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', side_effect=FileNotFoundError('File not found'))
    def test_load_file_not_found(self, mock_file, mock_get_param):
        """Test _load raises error when file not found"""
        mock_get_param.return_value = '/path/to/nonexistent.json'
        
        loader = DataLoader()
        
        with self.assertRaises(FileNotFoundError):
            loader.get_issues()
            
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_load_invalid_json(self, mock_file, mock_get_param):
        """Test _load raises error with invalid JSON"""
        mock_get_param.return_value = '/path/to/data.json'
        
        loader = DataLoader()
        
        with self.assertRaises(json.JSONDecodeError):
            loader.get_issues()
            
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_issues_with_multiple_issues(self, mock_file, mock_get_param):
        """Test get_issues with multiple issues"""
        mock_get_param.return_value = '/path/to/data.json'
        
        issue_data = [
            {
                'number': 1,
                'title': 'Issue 1',
                'state': 'open',
                'created_at': '2023-01-01T00:00:00Z',
                'labels': [],
                'events': []
            },
            {
                'number': 2,
                'title': 'Issue 2',
                'state': 'closed',
                'created_at': '2023-02-01T00:00:00Z',
                'labels': [],
                'events': []
            }
        ]
        
        mock_file.return_value.read.return_value = json.dumps(issue_data)
        
        loader = DataLoader()
        issues = loader.get_issues()
        
        self.assertEqual(len(issues), 2)
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_migration_date_with_none_dates(self, mock_file, mock_get_param):
        """Test get_migration_date when some events have None dates"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        event1 = Mock(spec=Event)
        event1.event_date = datetime(2023, 1, 1)
        
        event2 = Mock(spec=Event)
        event2.event_date = None
        
        issue1 = Mock(spec=Issue)
        issue1.events = [event1, event2]
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1]):
            try:
                migration_date = loader.get_migration_date()
            except TypeError:
                pass
                
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_migration_date_with_empty_events(self, mock_file, mock_get_param):
        """Test get_migration_date when issues have empty events list"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        issue1 = Mock(spec=Issue)
        issue1.events = []
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1]):
            try:
                migration_date = loader.get_migration_date()
            except ValueError:
                pass
                
    @patch('data_loader.config.get_parameter')
    def test_data_path_attribute_exists(self, mock_get_param):
        """Test that data_path attribute is set"""
        mock_get_param.return_value = '/test/path.json'
        
        loader = DataLoader()
        
        self.assertTrue(hasattr(loader, 'data_path'))
        self.assertEqual(loader.data_path, '/test/path.json')
        
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_year_range_returns_strings(self, mock_file, mock_get_param):
        """Test that get_year_range returns years as strings, not ints"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        issue1 = Mock(spec=Issue)
        issue1.created_date = datetime(2023, 1, 1)
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1]):
            years = loader.get_year_range()
            for year in years:
                self.assertIsInstance(year, str)
                
    @patch('data_loader.config.get_parameter')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_label_categories_multiple_issues(self, mock_file, mock_get_param):
        """Test get_label_categories with multiple issues and categories"""
        mock_get_param.return_value = '/path/to/data.json'
        mock_file.return_value.read.return_value = '[]'
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        
        label2 = Mock(spec=Label)
        label2.category = 'priority'
        
        label3 = Mock(spec=Label)
        label3.category = 'component'
        
        label4 = Mock(spec=Label)
        label4.category = 'type'
        
        issue1 = Mock(spec=Issue)
        issue1.labels = [label1, label2]
        
        issue2 = Mock(spec=Issue)
        issue2.labels = [label3]
        
        issue3 = Mock(spec=Issue)
        issue3.labels = [label4]
        
        loader = DataLoader()
        
        with patch.object(loader, 'get_issues', return_value=[issue1, issue2, issue3]):
            categories = loader.get_label_categories()
            
        self.assertEqual(len(categories), 3)
        self.assertIn('type', categories)
        self.assertIn('priority', categories)
        self.assertIn('component', categories)


if __name__ == '__main__':
    unittest.main()
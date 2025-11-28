import unittest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from analyses import Analysis1, Analysis2, Analysis3, COLORS
    from model import Issue, Label
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    raise


class TestAnalysis1(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_loader = Mock()
        self.mock_loader.get_label_categories.return_value = ['type', 'priority', 'component']
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_init_with_valid_category(self, mock_config, mock_dataloader_class):
        """Test initialization with valid category"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis1()
        
        self.assertEqual(analyses.CATEGORY, 'type')
        self.assertEqual(analyses.OTHER_CUTOUT, 0.05)
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('builtins.input', side_effect=['priority'])
    def test_init_with_empty_category(self, mock_input, mock_config, mock_dataloader_class):
        """Test initialization prompts for category when empty"""
        mock_config.side_effect = lambda key, default=None: '' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis1()
        
        self.assertEqual(analyses.CATEGORY, 'priority')
        mock_input.assert_called_once()
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('builtins.input', side_effect=['invalid', 'type'])
    def test_set_category_with_invalid_then_valid(self, mock_input, mock_config, mock_dataloader_class):
        """Test set_category handles invalid then valid input"""
        mock_config.side_effect = lambda key, default=None: 'invalid_cat' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis1()
        
        self.assertEqual(analyses.CATEGORY, 'type')
        self.assertEqual(mock_input.call_count, 2)
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_set_category_directly(self, mock_config, mock_dataloader_class):
        """Test set_category method directly"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis1()
        analyses.set_category('priority')
        
        self.assertEqual(analyses.CATEGORY, 'priority')
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_with_no_issues(self, mock_show, mock_config, mock_dataloader_class):
        """Test run method with no issues"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 1)
        self.mock_loader.get_issues.return_value = []
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis1()
        try:
            analyses.run()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly with empty issues list")
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_with_issues_no_labels(self, mock_show, mock_config, mock_dataloader_class):
        """Test run with issues that have no labels"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 1)
        
        issue1 = Mock(spec=Issue)
        issue1.state = 'open'
        issue1.created_date = datetime(2023, 12, 1)
        issue1.labels = []
        issue1.closed_date = None
        
        self.mock_loader.get_issues.return_value = [issue1]
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis1()
        try:
            analyses.run()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly with no labels")
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_with_none_sublabel(self, mock_show, mock_config, mock_dataloader_class):
        """Test run with labels that have None sublabel"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 1)

        label1 = Mock(spec=Label)
        label1.category = 'type'
        
        issue1 = Mock(spec=Issue)
        issue1.state = 'open'
        issue1.created_date = datetime(2023, 12, 1)
        issue1.labels = [label1]
        issue1.closed_date = None

        with patch('analyses.getattr', side_effect=lambda obj, attr, default: 'type' if attr == 'category' else default):
            self.mock_loader.get_issues.return_value = [issue1]
            self.mock_loader.get_migration_date.return_value = max_date
            
            analyses = Analysis1()
            
            try:
                analyses.run()
            except Exception as e:
                self.fail(f"run() raised {type(e).__name__} unexpectedly with None sublabel")
    
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_other_cutout_default_value(self, mock_config, mock_dataloader_class):
        """Test that OTHER_CUTOUT uses default value when not in config"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else default
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis1()

        self.assertIsNotNone(analyses.OTHER_CUTOUT)
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_other_cutout_zero_value(self, mock_config, mock_dataloader_class):
        """Test OTHER_CUTOUT with zero value"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (0 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis1()
        
        self.assertEqual(analyses.OTHER_CUTOUT, 0.0)
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('builtins.input', side_effect=[''])
    def test_set_category_multiple_empty_inputs(self, mock_input, mock_config, mock_dataloader_class):
        """Test set_category with multiple empty inputs creates infinite loop scenario"""
        mock_config.side_effect = lambda key, default=None: '' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        with self.assertRaises(StopIteration):
            analyses = Analysis1()
    
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    @patch('analyses.pd.DataFrame.plot')
    @patch('builtins.print')
    def test_run_with_valid_open_issues_creates_plot(self, mock_print, mock_plot, mock_show, mock_config, mock_dataloader_class):
        """Test run with valid open issues to cover histogram plot creation"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 1)
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        label1.sublabel = 'bug'
        
        label2 = Mock(spec=Label)
        label2.category = 'type'
        label2.sublabel = 'feature'
        
        open_issues = []
        for i in range(20):
            issue = Mock(spec=Issue)
            issue.state = 'open'
            issue.created_date = datetime(2023, 12, 1) + timedelta(days=i)
            issue.labels = [label1 if i % 2 == 0 else label2]
            issue.closed_date = None
            open_issues.append(issue)
        
        self.mock_loader.get_issues.return_value = open_issues
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis1()
        
        mock_plot.return_value = Mock()
        
        try:
            analyses.run()
            self.assertTrue(mock_plot.called)
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly: {e}")
    
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    @patch('analyses.pd.DataFrame.plot')
    @patch('builtins.print')
    def test_run_with_valid_closed_issues_creates_plot(self, mock_print, mock_plot, mock_show, mock_config, mock_dataloader_class):
        """Test run with valid closed issues to cover histogram plot creation"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 1)
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        label1.sublabel = 'bug'
        
        label2 = Mock(spec=Label)
        label2.category = 'type'
        label2.sublabel = 'feature'
        
        closed_issues = []
        for i in range(20):
            issue = Mock(spec=Issue)
            issue.state = 'closed'
            issue.created_date = datetime(2023, 11, 1) + timedelta(days=i)
            issue.closed_date = datetime(2023, 12, 1) + timedelta(days=i)
            issue.labels = [label1 if i % 2 == 0 else label2]
            closed_issues.append(issue)
        
        self.mock_loader.get_issues.return_value = closed_issues
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis1()
        
        mock_plot.return_value = Mock()
        
        try:
            analyses.run()
            self.assertTrue(mock_plot.called)
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly: {e}")
    
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    @patch('analyses.pd.DataFrame.plot')
    @patch('builtins.print')
    def test_run_with_both_open_and_closed_issues(self, mock_print, mock_plot, mock_show, mock_config, mock_dataloader_class):
        """Test run with both open and closed issues to cover all plot paths"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (5 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 1)
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        label1.sublabel = 'bug'
        
        label2 = Mock(spec=Label)
        label2.category = 'type'
        label2.sublabel = 'feature'
        
        issues = []
        for i in range(20):
            issue = Mock(spec=Issue)
            if i % 2 == 0:
                issue.state = 'open'
                issue.closed_date = None
            else:
                issue.state = 'closed'
                issue.closed_date = datetime(2023, 12, 1) + timedelta(days=i)
            issue.created_date = datetime(2023, 11, 1) + timedelta(days=i)
            issue.labels = [label1 if i % 3 == 0 else label2]
            issues.append(issue)
        
        self.mock_loader.get_issues.return_value = issues
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis1()
        
        mock_plot.return_value = Mock()
        
        try:
            analyses.run()
            self.assertTrue(mock_plot.called)
            mock_show.assert_called_once()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly: {e}")
    
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    @patch('analyses.pd.DataFrame.plot')
    @patch('builtins.print')
    def test_run_with_other_category_grouping(self, mock_print, mock_plot, mock_show, mock_config, mock_dataloader_class):
        """Test run with issues that trigger 'other' grouping due to cutout threshold"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (10 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 1)
        
        label_bug = Mock(spec=Label)
        label_bug.category = 'type'
        label_bug.sublabel = 'bug'
        
        label_rare1 = Mock(spec=Label)
        label_rare1.category = 'type'
        label_rare1.sublabel = 'rare1'
        
        label_rare2 = Mock(spec=Label)
        label_rare2.category = 'type'
        label_rare2.sublabel = 'rare2'
        
        issues = []
        for i in range(30):
            issue = Mock(spec=Issue)
            issue.state = 'open'
            issue.created_date = datetime(2023, 12, 1) + timedelta(days=i)
            issue.closed_date = None
            
            if i < 25:
                issue.labels = [label_bug]
            elif i < 27:
                issue.labels = [label_rare1]
            else:
                issue.labels = [label_rare2]
            
            issues.append(issue)
        
        self.mock_loader.get_issues.return_value = issues
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis1()
        
        mock_plot.return_value = Mock()
        
        try:
            analyses.run()
            self.assertTrue(mock_plot.called)
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly: {e}")

class TestAnalysis2(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_loader = Mock()
        self.mock_loader.get_label_categories.return_value = ['type', 'priority']
        self.mock_loader.get_year_range.return_value = ['2022', '2023', '2024']
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_init_with_valid_params(self, mock_config, mock_dataloader_class):
        """Test initialization with valid parameters"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else '2023'
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis2()
        
        self.assertEqual(analyses.CATEGORY, 'type')
        self.assertEqual(analyses.ISSUE_YEAR, '2023')
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('builtins.input', side_effect=['2023'])
    def test_init_with_empty_year(self, mock_input, mock_config, mock_dataloader_class):
        """Test initialization with empty year prompts user"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else ''
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis2()
        
        self.assertEqual(analyses.ISSUE_YEAR, '2023')
        mock_input.assert_called_once()
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('builtins.input', side_effect=['invalid', '2023'])
    def test_set_year_with_invalid_then_valid(self, mock_input, mock_config, mock_dataloader_class):
        """Test set_year handles invalid then valid input"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else 'invalid_year'
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis2()
        
        self.assertEqual(analyses.ISSUE_YEAR, '2023')
        self.assertEqual(mock_input.call_count, 2)
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_set_year_all(self, mock_config, mock_dataloader_class):
        """Test set_year with 'all' option"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else 'all'
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis2()
        
        self.assertEqual(analyses.ISSUE_YEAR, 'all')
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_set_year_numeric(self, mock_config, mock_dataloader_class):
        """Test set_year with numeric year"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else 2023
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis2()
        
        self.assertEqual(analyses.ISSUE_YEAR, '2023')
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_with_no_issues(self, mock_show, mock_config, mock_dataloader_class):
        """Test run method with no issues"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else '2023'
        mock_dataloader_class.return_value = self.mock_loader
        
        self.mock_loader.get_issues.return_value = []
        
        analyses = Analysis2()
        
        try:
            analyses.run()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly with no issues")
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_with_issues_no_created_date(self, mock_show, mock_config, mock_dataloader_class):
        """Test run with issues missing created_date"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else '2023'
        mock_dataloader_class.return_value = self.mock_loader
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        label1.sublabel = 'bug'
        
        issue1 = Mock(spec=Issue)
        issue1.created_date = None
        issue1.labels = [label1]
        
        self.mock_loader.get_issues.return_value = [issue1]
        
        analyses = Analysis2()
        try:
            analyses.run()
        except AttributeError:
            pass 
        except Exception as e:
            pass
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_filters_by_year_correctly(self, mock_show, mock_config, mock_dataloader_class):
        """Test that run filters issues by year correctly"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else '2023'
        mock_dataloader_class.return_value = self.mock_loader
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        label1.sublabel = 'bug'
        

        issue1 = Mock(spec=Issue)
        issue1.created_date = datetime(2023, 6, 15)
        issue1.labels = [label1]
        

        issue2 = Mock(spec=Issue)
        issue2.created_date = datetime(2022, 6, 15)
        issue2.labels = [label1]
        
        self.mock_loader.get_issues.return_value = [issue1, issue2]
        
        analyses = Analysis2()
        
        try:
            analyses.run()
            mock_show.assert_called_once()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly")
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_with_all_years_includes_all(self, mock_show, mock_config, mock_dataloader_class):
        """Test that 'all' includes all years"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else 'all'
        mock_dataloader_class.return_value = self.mock_loader
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        label1.sublabel = 'bug'
        
        issue1 = Mock(spec=Issue)
        issue1.created_date = datetime(2023, 6, 15)
        issue1.labels = [label1]
        
        issue2 = Mock(spec=Issue)
        issue2.created_date = datetime(2022, 6, 15)
        issue2.labels = [label1]
        
        self.mock_loader.get_issues.return_value = [issue1, issue2]
        
        analyses = Analysis2()
        
        try:
            analyses.run()
            mock_show.assert_called_once()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly")
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_with_empty_labels_list(self, mock_show, mock_config, mock_dataloader_class):
        """Test run with issues having empty labels list"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else '2023'
        mock_dataloader_class.return_value = self.mock_loader
        
        issue1 = Mock(spec=Issue)
        issue1.created_date = datetime(2023, 6, 15)
        issue1.labels = []  # Empty labels
        
        self.mock_loader.get_issues.return_value = [issue1]
        
        analyses = Analysis2()
        

        try:
            analyses.run()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly")
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')  
    def test_run_with_wrong_category_labels(self, mock_show, mock_config, mock_dataloader_class):
        """Test run with labels from different category"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else '2023'
        mock_dataloader_class.return_value = self.mock_loader
        
        label1 = Mock(spec=Label)
        label1.category = 'priority'
        label1.sublabel = 'high'
        
        issue1 = Mock(spec=Issue)
        issue1.created_date = datetime(2023, 6, 15)
        issue1.labels = [label1]
        
        self.mock_loader.get_issues.return_value = [issue1]
        
        analyses = Analysis2()
        
        try:
            analyses.run()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly")
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_set_category_directly(self, mock_config, mock_dataloader_class):
        """Test set_category method directly"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else '2023'
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis2()
        analyses.set_category('priority')
        
        self.assertEqual(analyses.CATEGORY, 'priority')
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_set_year_directly(self, mock_config, mock_dataloader_class):
        """Test set_year method directly"""
        mock_config.side_effect = lambda key: 'type' if key == 'category' else '2023'
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis2()
        analyses.set_year('2024')
        
        self.assertEqual(analyses.ISSUE_YEAR, '2024')


class TestAnalysis3(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_loader = Mock()
        self.mock_loader.get_label_categories.return_value = ['type', 'priority']
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_init_with_valid_category(self, mock_config, mock_dataloader_class):
        """Test initialization with valid category"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (2 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis3()
        
        self.assertEqual(analyses.CATEGORY, 'type')
        self.assertEqual(analyses.OTHER_CUTOUT, 0.02)
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('builtins.input', side_effect=['priority'])
    def test_init_with_empty_category(self, mock_input, mock_config, mock_dataloader_class):
        """Test initialization with empty category"""
        mock_config.side_effect = lambda key, default=None: '' if key == 'category' else (2 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis3()
        
        self.assertEqual(analyses.CATEGORY, 'priority')
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_with_no_issues(self, mock_show, mock_config, mock_dataloader_class):
        """Test run with no issues"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (2 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value =self.mock_loader
        
        max_date = datetime(2024, 1, 1)
        
        self.mock_loader.get_issues.return_value = []
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis3()
        
        try:
            analyses.run()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly with no issues")
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    def test_run_with_issues_no_labels(self, mock_show, mock_config, mock_dataloader_class):
        """Test run with issues having no labels"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (2 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 1)
        
        issue1 = Mock(spec=Issue)
        issue1.state = 'open'
        issue1.created_date = datetime(2023, 11, 1)
        issue1.closed_date = None
        issue1.labels = []
        
        self.mock_loader.get_issues.return_value = [issue1]
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis3()
        
        try:
            analyses.run()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly")
            
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_set_category_directly(self, mock_config, mock_dataloader_class):
        """Test set_category method"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (2 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis3()
        analyses.set_category('priority')
        
        self.assertEqual(analyses.CATEGORY, 'priority')
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    def test_other_cutout_calculation(self, mock_config, mock_dataloader_class):
        """Test OTHER_CUTOUT percentage calculation"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (10 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis3()
        
        self.assertEqual(analyses.OTHER_CUTOUT, 0.10)
        
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('builtins.input', side_effect=['invalid_cat', 'priority'])
    def test_init_with_invalid_category(self, mock_input, mock_config, mock_dataloader_class):
        """Test initialization with invalid category"""
        mock_config.side_effect = lambda key, default=None: 'invalid' if key == 'category' else (2 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        analyses = Analysis3()
        
        self.assertEqual(analyses.CATEGORY, 'priority')
        self.assertEqual(mock_input.call_count, 2)

    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    @patch('analyses.pd.DataFrame.plot')
    def test_run_with_multiple_labels_over_time(self, mock_plot, mock_show, mock_config, mock_dataloader_class):
        """Test run with multiple labels to cover area plot creation"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (2 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 15)
        
        label_bug = Mock(spec=Label)
        label_bug.category = 'type'
        label_bug.sublabel = 'bug'
        
        label_feature = Mock(spec=Label)
        label_feature.category = 'type'
        label_feature.sublabel = 'feature'
        
        issues = []
        
        for i in range(30):
            issue = Mock(spec=Issue)
            issue.created_date = datetime(2023, 12, 1) + timedelta(days=i)
            if i < 15:
                issue.state = 'closed'
                issue.closed_date = datetime(2024, 1, 1) + timedelta(days=i)
            else:
                issue.state = 'open'
                issue.closed_date = None
            issue.labels = [label_bug]
            issues.append(issue)
        
        for i in range(20):
            issue = Mock(spec=Issue)
            issue.created_date = datetime(2023, 12, 5) + timedelta(days=i)
            if i < 10:
                issue.state = 'closed'
                issue.closed_date = datetime(2024, 1, 5) + timedelta(days=i)
            else:
                issue.state = 'open'
                issue.closed_date = None
            issue.labels = [label_feature]
            issues.append(issue)
        
        self.mock_loader.get_issues.return_value = issues
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis3()
        
        mock_area_plot = Mock()
        mock_plot.area.return_value = mock_area_plot
        
        try:
            analyses.run()
            mock_show.assert_called_once()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly: {e}")
    
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    @patch('analyses.pd.DataFrame.plot')
    def test_run_with_other_category_in_area_plot(self, mock_plot, mock_show, mock_config, mock_dataloader_class):
        """Test run where rare labels get grouped into 'other' category"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (10 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 15)
        
        label_common = Mock(spec=Label)
        label_common.category = 'type'
        label_common.sublabel = 'common'
        
        label_rare = Mock(spec=Label)
        label_rare.category = 'type'
        label_rare.sublabel = 'rare'
        
        issues = []
        
        for i in range(50):
            issue = Mock(spec=Issue)
            issue.created_date = datetime(2023, 12, 1) + timedelta(days=i % 30)
            issue.state = 'open' if i % 3 == 0 else 'closed'
            issue.closed_date = None if issue.state == 'open' else datetime(2024, 1, 1) + timedelta(days=i % 20)
            issue.labels = [label_common]
            issues.append(issue)
        
        for i in range(3):
            issue = Mock(spec=Issue)
            issue.created_date = datetime(2023, 12, 10) + timedelta(days=i)
            issue.state = 'open'
            issue.closed_date = None
            issue.labels = [label_rare]
            issues.append(issue)
        
        self.mock_loader.get_issues.return_value = issues
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis3()
        
        mock_area_plot = Mock()
        mock_plot.area.return_value = mock_area_plot
        
        try:
            analyses.run()
            mock_show.assert_called_once()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly: {e}")
    
    @patch('analyses.DataLoader')
    @patch('analyses.config.get_parameter')
    @patch('analyses.plt.show')
    @patch('analyses.pd.DataFrame.plot')
    def test_run_with_date_range_computation(self, mock_plot, mock_show, mock_config, mock_dataloader_class):
        """Test run to ensure date range and counts computation is executed"""
        mock_config.side_effect = lambda key, default=None: 'type' if key == 'category' else (2 if key == 'other_cutout' else default)
        mock_dataloader_class.return_value = self.mock_loader
        
        max_date = datetime(2024, 1, 10)
        
        label1 = Mock(spec=Label)
        label1.category = 'type'
        label1.sublabel = 'label1'
        
        label2 = Mock(spec=Label)
        label2.category = 'type'
        label2.sublabel = 'label2'
        
        issues = []
        for i in range(25):
            issue = Mock(spec=Issue)
            issue.created_date = datetime(2024, 1, 1)
            issue.state = 'closed'
            issue.closed_date = datetime(2024, 1, 5)
            issue.labels = [label1]
            issues.append(issue)
        
        for i in range(15):
            issue = Mock(spec=Issue)
            issue.created_date = datetime(2024, 1, 3)
            issue.state = 'open'
            issue.closed_date = None
            issue.labels = [label2]
            issues.append(issue)
        
        self.mock_loader.get_issues.return_value = issues
        self.mock_loader.get_migration_date.return_value = max_date
        
        analyses = Analysis3()
        
        mock_area_plot = Mock()
        mock_plot.area.return_value = mock_area_plot
        
        try:
            analyses.run()
            mock_show.assert_called_once()
        except Exception as e:
            self.fail(f"run() raised {type(e).__name__} unexpectedly: {e}")

class TestColorConstants(unittest.TestCase):
    """Test the COLORS constant"""
    
    def test_colors_list_exists(self):
        """Test that COLORS list is defined"""
        self.assertIsNotNone(COLORS)
        
    def test_colors_list_length(self):
        """Test that COLORS has expected number of colors"""
        self.assertEqual(len(COLORS), 10)
        
    def test_colors_are_strings(self):
        """Test that all colors are strings"""
        for color in COLORS:
            self.assertIsInstance(color, str)
            
    def test_colors_are_hex_format(self):
        """Test that colors are in hex format"""
        for color in COLORS:
            self.assertTrue(color.startswith('#'))
            self.assertEqual(len(color), 7)

if __name__ == '__main__':
    unittest.main()
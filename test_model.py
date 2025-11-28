import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import State, Event, Label, Issue


class TestState(unittest.TestCase):
    """Test the State enum"""
    
    def test_state_open(self):
        """Test State.open value"""
        self.assertEqual(State.open, 'open')
        self.assertEqual(State.open.value, 'open')
        
    def test_state_closed(self):
        """Test State.closed value"""
        self.assertEqual(State.closed, 'closed')
        self.assertEqual(State.closed.value, 'closed')
        
    def test_state_is_string_enum(self):
        """Test that State is a string enum"""
        self.assertIsInstance(State.open, str)
        self.assertIsInstance(State.closed, str)
        
    def test_state_comparison(self):
        """Test State enum comparison"""
        self.assertEqual(State.open, State['open'])
        self.assertEqual(State.closed, State['closed'])


class TestEvent(unittest.TestCase):
    """Test the Event class"""
    
    def test_init_with_none(self):
        """Test Event initialization with None"""
        event = Event(None)
        
        self.assertIsNone(event.event_type)
        self.assertIsNone(event.author)
        self.assertIsNone(event.event_date)
        self.assertIsNone(event.label)
        self.assertIsNone(event.comment)
        
    def test_init_with_empty_dict(self):
        """Test Event initialization with empty dict"""
        event = Event({})
        
        self.assertIsNone(event.event_type)
        self.assertIsNone(event.author)
        self.assertIsNone(event.event_date)
        self.assertIsNone(event.label)
        self.assertIsNone(event.comment)
        
    def test_init_with_full_data(self):
        """Test Event initialization with complete data"""
        jobj = {
            'event_type': 'closed',
            'author': 'user123',
            'event_date': '2023-06-15T10:30:00Z',
            'label': 'bug',
            'comment': 'Fixed the issue'
        }
        
        event = Event(jobj)
        
        self.assertEqual(event.event_type, 'closed')
        self.assertEqual(event.author, 'user123')
        self.assertIsInstance(event.event_date, datetime)
        self.assertEqual(event.label, 'bug')
        self.assertEqual(event.comment, 'Fixed the issue')
        
    def test_init_with_partial_data(self):
        """Test Event initialization with partial data"""
        jobj = {
            'event_type': 'labeled',
            'author': 'user456'
        }
        
        event = Event(jobj)
        
        self.assertEqual(event.event_type, 'labeled')
        self.assertEqual(event.author, 'user456')
        self.assertIsNone(event.event_date)
        self.assertIsNone(event.label)
        self.assertIsNone(event.comment)
        
    def test_from_json_with_invalid_date(self):
        """Test from_json with invalid date string"""
        jobj = {
            'event_type': 'comment',
            'event_date': 'invalid-date-format',
            'comment': 'Test comment'
        }
        
        event = Event(jobj)
        self.assertIsNone(event.event_date)
        self.assertEqual(event.event_type, 'comment')
        
    def test_from_json_with_none_date(self):
        """Test from_json with None date"""
        jobj = {
            'event_type': 'reopened',
            'event_date': None
        }
        
        event = Event(jobj)
        
        self.assertIsNone(event.event_date)
        
    def test_from_json_valid_iso_date(self):
        """Test from_json with valid ISO date"""
        jobj = {
            'event_date': '2023-12-25T15:45:30Z'
        }
        
        event = Event(jobj)
        
        self.assertIsInstance(event.event_date, datetime)
        self.assertEqual(event.event_date.year, 2023)
        self.assertEqual(event.event_date.month, 12)
        self.assertEqual(event.event_date.day, 25)


class TestLabel(unittest.TestCase):
    """Test the Label class"""
    
    def test_init_with_category_and_sublabel(self):
        """Test Label initialization with category/sublabel format"""
        label = Label('type/bug')
        
        self.assertEqual(label.category, 'type')
        self.assertEqual(label.sublabel, 'bug')
        
    def test_init_with_only_category(self):
        """Test Label initialization with only category"""
        label = Label('priority')
        
        self.assertEqual(label.category, 'priority')
        self.assertEqual(label.sublabel, '')
        
    def test_init_with_multiple_slashes(self):
        """Test Label initialization with multiple slashes"""
        label = Label('type/bug/critical')
        self.assertEqual(label.category, 'type')
        self.assertEqual(label.sublabel, 'bug/critical')
        
    def test_init_with_empty_string(self):
        """Test Label initialization with empty string"""
        label = Label('')
        
        self.assertEqual(label.category, '')
        self.assertEqual(label.sublabel, '')
        
    def test_full_label_with_sublabel(self):
        """Test full_label method with sublabel"""
        label = Label('type/feature')
        
        result = label.full_label()
        
        self.assertEqual(result, 'type/feature')
        
    def test_full_label_without_sublabel(self):
        """Test full_label method without sublabel"""
        label = Label('priority')
        
        result = label.full_label()
        self.assertTrue('priority' in result)
        
    def test_full_label_with_empty_sublabel(self):
        """Test full_label with explicitly empty sublabel"""
        label = Label('component')
        label.sublabel = ''
        
        result = label.full_label()
        self.assertIsNotNone(result)


class TestIssue(unittest.TestCase):
    """Test the Issue class"""
    
    def test_init_with_none(self):
        """Test Issue initialization with None"""
        issue = Issue(None)
        
        self.assertIsNone(issue.url)
        self.assertIsNone(issue.creator)
        self.assertEqual(issue.labels, [])
        self.assertIsNone(issue.state)
        self.assertEqual(issue.assignees, [])
        self.assertIsNone(issue.title)
        self.assertIsNone(issue.text)
        self.assertEqual(issue.number, -1)
        self.assertIsNone(issue.created_date)
        self.assertIsNone(issue.updated_date)
        self.assertIsNone(issue.timeline_url)
        self.assertEqual(issue.events, [])
        self.assertIsNone(issue.closed_date)
        
    def test_init_without_args(self):
        """Test Issue initialization without arguments"""
        issue = Issue()
        
        self.assertEqual(issue.number, -1)
        self.assertEqual(issue.labels, [])
        self.assertEqual(issue.events, [])
        
    def test_init_with_full_data(self):
        """Test Issue initialization with complete data"""
        jobj = {
            'url': 'https://github.com/test/repo/issues/1',
            'creator': 'user123',
            'labels': ['type/bug', 'priority/high'],
            'state': 'open',
            'assignees': ['dev1', 'dev2'],
            'title': 'Test Issue',
            'text': 'Issue description',
            'number': '42',
            'created_date': '2023-01-01T00:00:00Z',
            'updated_date': '2023-01-02T00:00:00Z',
            'timeline_url': 'https://github.com/test/repo/issues/1/timeline',
            'events': []
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(issue.url, 'https://github.com/test/repo/issues/1')
        self.assertEqual(issue.creator, 'user123')
        self.assertEqual(len(issue.labels), 2)
        self.assertEqual(issue.state, State.open)
        self.assertEqual(issue.assignees, ['dev1', 'dev2'])
        self.assertEqual(issue.title, 'Test Issue')
        self.assertEqual(issue.text, 'Issue description')
        self.assertEqual(issue.number, 42)
        self.assertIsInstance(issue.created_date, datetime)
        self.assertIsInstance(issue.updated_date, datetime)
        
    def test_from_json_with_invalid_number(self):
        """Test from_json with invalid number"""
        jobj = {
            'number': 'invalid',
            'state': 'open'
        }
        
        issue = Issue(jobj)
        self.assertEqual(issue.number, -1)
        
    def test_from_json_with_missing_number(self):
        """Test from_json with missing number"""
        jobj = {
            'state': 'open'
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(issue.number, -1)
        
    def test_from_json_with_invalid_created_date(self):
        """Test from_json with invalid created_date"""
        jobj = {
            'state': 'open',
            'created_date': 'not-a-date'
        }
        
        issue = Issue(jobj)
        
        self.assertIsNone(issue.created_date)
        
    def test_from_json_with_invalid_updated_date(self):
        """Test from_json with invalid updated_date"""
        jobj = {
            'state': 'open',
            'updated_date': 'invalid-date'
        }
        
        issue = Issue(jobj)
        
        self.assertIsNone(issue.updated_date)
        
    def test_from_json_creates_label_objects(self):
        """Test that from_json creates Label objects"""
        jobj = {
            'state': 'open',
            'labels': ['type/bug', 'priority/high', 'component']
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(len(issue.labels), 3)
        for label in issue.labels:
            self.assertIsInstance(label, Label)
            
    def test_from_json_creates_event_objects(self):
        """Test that from_json creates Event objects"""
        jobj = {
            'state': 'open',
            'events': [
                {'event_type': 'labeled', 'label': 'bug'},
                {'event_type': 'commented', 'comment': 'Test'}
            ]
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(len(issue.events), 2)
        for event in issue.events:
            self.assertIsInstance(event, Event)
            
    def test_set_closed_date_for_open_issue(self):
        """Test set_closed_date returns False for open issue"""
        issue = Issue()
        issue.state = 'open'
        issue.events = []
        
        result = issue.set_closed_date()
        
        self.assertFalse(result)
        
    def test_set_closed_date_with_closed_event(self):
        """Test set_closed_date sets date from closed event"""
        jobj = {
            'state': 'closed',
            'events': [
                {'event_type': 'closed', 'event_date': '2023-06-15T10:00:00Z'}
            ]
        }
        
        issue = Issue(jobj)
        
        self.assertIsNotNone(issue.closed_date)
        self.assertIsInstance(issue.closed_date, datetime)
        
    def test_set_closed_date_with_multiple_closed_events(self):
        """Test set_closed_date picks latest closed event"""
        jobj = {
            'state': 'closed',
            'events': [
                {'event_type': 'closed', 'event_date': '2023-06-15T10:00:00Z'},
                {'event_type': 'closed', 'event_date': '2023-07-20T15:00:00Z'}
            ]
        }
        
        issue = Issue(jobj)
        
        self.assertIsNotNone(issue.closed_date)
        self.assertEqual(issue.closed_date.month, 7)
        
    def test_set_closed_date_with_reopen_after_close(self):
        """Test set_closed_date returns False when reopened after close"""
        jobj = {
            'state': 'closed',
            'events': [
                {'event_type': 'closed', 'event_date': '2023-06-15T10:00:00Z'},
                {'event_type': 'reopened', 'event_date': '2023-06-20T12:00:00Z'}
            ]
        }
        
        issue = Issue(jobj)
        self.assertIsNone(issue.closed_date)
        
    def test_set_closed_date_with_close_after_reopen(self):
        """Test set_closed_date handles close after reopen"""
        jobj = {
            'state': 'closed',
            'events': [
                {'event_type': 'closed', 'event_date': '2023-06-15T10:00:00Z'},
                {'event_type': 'reopened', 'event_date': '2023-06-20T12:00:00Z'},
                {'event_type': 'closed', 'event_date': '2023-06-25T14:00:00Z'}
            ]
        }
        
        issue = Issue(jobj)
        
        self.assertIsNotNone(issue.closed_date)
        # Should be the final close date
        self.assertEqual(issue.closed_date.day, 25)
        
    def test_set_closed_date_with_no_events(self):
        """Test set_closed_date with closed issue but no events"""
        jobj = {
            'state': 'closed',
            'events': []
        }
        
        issue = Issue(jobj)
        self.assertIsNone(issue.closed_date)
        
    def test_set_closed_date_with_none_event_dates(self):
        """Test set_closed_date with events that have None dates"""
        jobj = {
            'state': 'closed',
            'events': [
                {'event_type': 'closed', 'event_date': None}
            ]
        }
        
        issue = Issue(jobj)
        self.assertIsNone(issue.closed_date)
        
    def test_from_json_with_empty_labels(self):
        """Test from_json with empty labels list"""
        jobj = {
            'state': 'open',
            'labels': []
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(issue.labels, [])
        
    def test_from_json_with_missing_labels(self):
        """Test from_json when labels key is missing"""
        jobj = {
            'state': 'open'
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(issue.labels, [])
        
    def test_from_json_with_empty_events(self):
        """Test from_json with empty events list"""
        jobj = {
            'state': 'open',
            'events': []
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(issue.events, [])
        
    def test_from_json_with_missing_events(self):
        """Test from_json when events key is missing"""
        jobj = {
            'state': 'open'
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(issue.events, [])
        
    def test_from_json_with_missing_assignees(self):
        """Test from_json when assignees key is missing"""
        jobj = {
            'state': 'open'
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(issue.assignees, [])
        
    def test_state_enum_assignment(self):
        """Test that state is assigned as State enum"""
        jobj = {
            'state': 'closed'
        }
        
        issue = Issue(jobj)
        
        self.assertEqual(issue.state, State.closed)
        self.assertIsInstance(issue.state, State)
        
    def test_from_json_with_all_optional_fields_missing(self):
        """Test from_json with minimal data"""
        jobj = {
            'state': 'open'
        }
        
        issue = Issue(jobj)
        self.assertEqual(issue.state, State.open)
        self.assertEqual(issue.number, -1)
        self.assertEqual(issue.labels, [])
        self.assertEqual(issue.events, [])
        self.assertEqual(issue.assignees, [])
        
    def test_set_closed_date_mixed_event_types(self):
        """Test set_closed_date with various event types"""
        jobj = {
            'state': 'closed',
            'events': [
                {'event_type': 'labeled', 'event_date': '2023-06-01T10:00:00Z'},
                {'event_type': 'closed', 'event_date': '2023-06-15T10:00:00Z'},
                {'event_type': 'commented', 'event_date': '2023-06-16T10:00:00Z'}
            ]
        }
        
        issue = Issue(jobj)
        self.assertIsNotNone(issue.closed_date)
        self.assertEqual(issue.closed_date.day, 15)
        
    def test_set_closed_date_filters_none_dates_correctly(self):
        """Test that set_closed_date filters events with None dates"""
        jobj = {
            'state': 'closed',
            'events': [
                {'event_type': 'closed', 'event_date': None},
                {'event_type': 'closed', 'event_date': '2023-06-15T10:00:00Z'}
            ]
        }
        
        issue = Issue(jobj)
        self.assertIsNotNone(issue.closed_date)
        self.assertEqual(issue.closed_date.day, 15)


if __name__ == '__main__':
    unittest.main()
from unittest.mock import MagicMock

import praw


class MockStream:
    def __init__(self, data):
        self.data = data

    def submissions(self, skip_existing):
        return self.data

class MockSubs:
    def __init__(self, data):
        self.stream = MockStream(data)


class SubmissionMock:
    def __init__(self, data):
        self.data = data

    def subreddit(self, subreddits):
        return MockSubs(self.data)


def create_submission(display_name='test', title='test title'):
    mockSub = MagicMock(spec=praw.models.Submission)
    mockSub.subreddit = MagicMock()
    mockSub.subreddit.display_name = display_name
    mockSub.subreddit.display_name_prefixed = 'r/' + display_name
    mockSub.title = title
    return mockSub

def create_reddit():
    mockReddit = MagicMock(praw.Reddit)
    return mockReddit

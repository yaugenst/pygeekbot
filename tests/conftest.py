import pytest
from datetime import datetime
from pygeekbot import GeekbotClient

MOCK_TEAM = {
    "id": 1234567,
    "name": "Test Team",
    "users": [
        {
            "id": "U123456789",
            "username": "testuser",
            "realname": "Test User",
            "profile_img": "https://example.com/avatar.jpg",
            "role": "member",
            "email": "test@example.com",
            "deleted": False,
        }
    ],
}

MOCK_STANDUP = {
    "id": 987654,
    "name": "testing",
    "channel": "testing",
    "time": "10:00:00",
    "timezone": "user_local",
    "days": [],
    "questions": [
        {
            "id": 11111,
            "text": "How do you feel today?",
            "color": "EEEEEE",
            "schedule": None,
            "answer_type": "text",
            "answer_choices": [],
            "hasAnswers": True,
            "is_random": False,
            "random_texts": [],
            "prefilled_by": None,
            "text_id": 20725,
            "preconditions": [],
            "label": "sentiment",
        },
        {
            "id": 22222,
            "text": "What have you done since {last_report_date}?",
            "color": "CEF1F3",
            "schedule": None,
            "answer_type": "text",
            "answer_choices": [],
            "hasAnswers": True,
            "is_random": False,
            "random_texts": [],
            "prefilled_by": 33333,
            "text_id": 43939,
            "preconditions": [],
            "label": "done",
        },
    ],
    "users": [
        {
            "id": "U123456789",
            "username": "testuser",
            "realname": "Test User",
            "profile_img": "https://example.com/avatar.jpg",
            "role": "member",
            "email": "test@example.com",
            "deleted": False,
        }
    ],
    "wait_time": -1,
    "personalised": False,
    "sync_channel_members": False,
}

MOCK_REPORT = {
    "id": 123456789,
    "standup_id": 987654,
    "slack_ts": "1234567890.123456",
    "timestamp": int(datetime.now().timestamp()),
    "channel": "testing",
    "member": {
        "id": "U123456789",
        "username": "testuser",
        "realname": "Test User",
        "profile_img": None,
        "role": None,
    },
    "questions": [
        {
            "id": 987654321,
            "question": "How do you feel today?",
            "question_id": 11111,
            "color": "EEEEEE",
            "answer": "Test answer for question 11111",
            "images": [],
            "html_formatted": False,
        }
    ],
}


@pytest.fixture
def client():
    """Create a GeekbotClient."""
    return GeekbotClient(api_key="test_api_key")

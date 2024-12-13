import pytest
from pygeekbot import GeekbotClient
from pygeekbot.models import ReportCreate, StandupUpdate
from .conftest import MOCK_TEAM, MOCK_STANDUP, MOCK_REPORT


@pytest.fixture
def client():
    """Create a GeekbotClient."""
    return GeekbotClient(api_key="test_api_key")


class TestTeamOperations:
    """Tests for team-related operations."""

    def test_get_team(self, client, httpx_mock):
        """Test getting team information."""
        httpx_mock.add_response(
            method="GET", url="https://api.geekbot.com/v1/teams", json=MOCK_TEAM
        )
        team = client.get_team()
        assert team.id == MOCK_TEAM["id"]
        assert team.name == MOCK_TEAM["name"]
        assert len(team.users) == len(MOCK_TEAM["users"])

    def test_get_team_unauthorized(self, client, httpx_mock):
        """Test getting team information with invalid API key."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geekbot.com/v1/teams",
            status_code=401,
            json={"error": "Unauthorized"},
        )
        with pytest.raises(Exception):
            client.get_team()


class TestStandupOperations:
    """Tests for standup-related operations."""

    def test_get_standups(self, client, httpx_mock):
        """Test getting all standups."""
        httpx_mock.add_response(
            method="GET", url="https://api.geekbot.com/v1/standups", json=[MOCK_STANDUP]
        )
        standups = client.get_standups()
        assert len(standups) == 1
        assert standups[0].id == MOCK_STANDUP["id"]
        assert standups[0].name == MOCK_STANDUP["name"]

    def test_find_standup_by_name(self, client, httpx_mock):
        """Test finding standup by name."""
        httpx_mock.add_response(
            method="GET", url="https://api.geekbot.com/v1/standups", json=[MOCK_STANDUP]
        )
        standup = client.find_standup_by_name("testing")
        assert standup is not None
        assert standup.id == MOCK_STANDUP["id"]
        assert standup.name == MOCK_STANDUP["name"]

    def test_find_standup_by_name_not_found(self, client, httpx_mock):
        """Test finding non-existent standup by name."""
        httpx_mock.add_response(
            method="GET", url="https://api.geekbot.com/v1/standups", json=[]
        )
        standup = client.find_standup_by_name("non_existent")
        assert standup is None

    def test_get_standup(self, client, httpx_mock):
        """Test getting specific standup."""
        httpx_mock.add_response(
            method="GET",
            url=f"https://api.geekbot.com/v1/standups/{MOCK_STANDUP['id']}",
            json=MOCK_STANDUP,
        )
        standup = client.get_standup(MOCK_STANDUP["id"])
        assert standup.id == MOCK_STANDUP["id"]
        assert standup.name == MOCK_STANDUP["name"]

    def test_update_standup(self, client, httpx_mock):
        """Test updating a standup."""
        httpx_mock.add_response(
            method="PATCH",
            url=f"https://api.geekbot.com/v1/standups/{MOCK_STANDUP['id']}",
            json={**MOCK_STANDUP, "name": "testing (updated)"},
        )
        updated = client.update_standup(
            MOCK_STANDUP["id"], StandupUpdate(name="testing (updated)")
        )
        assert updated.id == MOCK_STANDUP["id"]
        assert updated.name == "testing (updated)"

    def test_start_standup(self, client, httpx_mock):
        """Test starting a standup."""
        httpx_mock.add_response(
            method="POST",
            url=f"https://api.geekbot.com/v1/standups/{MOCK_STANDUP['id']}/start",
            text='"ok"',
        )
        result = client.start_standup(MOCK_STANDUP["id"])
        assert result == "ok"


class TestReportOperations:
    """Tests for report-related operations."""

    def test_get_reports(self, client, httpx_mock):
        """Test getting reports for a standup."""
        httpx_mock.add_response(
            method="GET",
            url=f"https://api.geekbot.com/v1/reports?standup_id={MOCK_STANDUP['id']}&limit=10",
            json=[MOCK_REPORT],
        )
        reports = client.get_reports(standup_id=MOCK_STANDUP["id"], limit=10)
        assert len(reports) == 1
        assert reports[0].id == MOCK_REPORT["id"]
        assert reports[0].standup_id == MOCK_REPORT["standup_id"]

    def test_create_report(self, client, httpx_mock):
        """Test creating a report."""
        httpx_mock.add_response(
            method="POST", url="https://api.geekbot.com/v1/reports", json=MOCK_REPORT
        )
        report = client.create_report(
            ReportCreate(
                standup_id=MOCK_STANDUP["id"],
                answers={
                    str(q["id"]): {"text": f"Test answer for question {q['id']}"}
                    for q in MOCK_STANDUP["questions"]
                },
            )
        )
        assert report.id == MOCK_REPORT["id"]
        assert report.standup_id == MOCK_REPORT["standup_id"]

    def test_create_report_invalid_data(self, client, httpx_mock):
        """Test creating a report with invalid data."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.geekbot.com/v1/reports",
            status_code=400,
            json={"error": "Invalid data"},
        )
        with pytest.raises(Exception):
            client.create_report(
                ReportCreate(
                    standup_id=-1,
                    answers={},
                )
            )

    @pytest.mark.parametrize(
        "limit,expected",
        [
            (1, 1),
            (5, 1),  # Assuming MOCK_REPORT is the only data
            (None, 1),
        ],
    )
    def test_get_reports_with_different_limits(
        self, client, httpx_mock, limit, expected
    ):
        """Test getting reports with different limit parameters."""
        url = "https://api.geekbot.com/v1/reports?standup_id={}&".format(
            MOCK_STANDUP["id"]
        )
        if limit is not None:
            url += f"limit={limit}"

        httpx_mock.add_response(method="GET", url=url, json=[MOCK_REPORT])
        reports = client.get_reports(standup_id=MOCK_STANDUP["id"], limit=limit)
        assert len(reports) == expected


class TestUserOperations:
    """Tests for user-related operations."""

    def test_get_user_reports(self, client, httpx_mock):
        """Test getting user reports."""
        user_id = MOCK_TEAM["users"][0]["id"]
        httpx_mock.add_response(
            method="GET",
            url=f"https://api.geekbot.com/v1/reports?limit=5&user_id={user_id}",
            json=[MOCK_REPORT],
        )
        reports = client.get_user_reports(user_id, limit=5)
        assert len(reports) == 1
        assert reports[0].id == MOCK_REPORT["id"]

    def test_get_user_standups(self, client, httpx_mock):
        """Test getting user standups."""
        user_id = MOCK_TEAM["users"][0]["id"]
        httpx_mock.add_response(
            method="GET",
            url="https://api.geekbot.com/v1/standups",
            json=[MOCK_STANDUP],
        )
        standups = client.get_user_standups(user_id)
        assert len(standups) == 1
        assert standups[0].id == MOCK_STANDUP["id"]

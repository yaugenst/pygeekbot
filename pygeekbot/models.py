from typing import List, Optional, Dict, Any
import msgspec


class ReportMember(msgspec.Struct, kw_only=True):
    """Member who submitted the report.

    Attributes
    ----------
    id : str
        Unique identifier of the member
    username : str
        Slack username of the member
    realname : str
        Full name of the member
    profile_img : str = None
        URL to the member's profile image
    role : str = None
        Role of the member in the team
    """

    id: str
    username: str
    realname: str
    profile_img: Optional[str] = None
    role: Optional[str] = None


class ReportQuestion(msgspec.Struct, kw_only=True):
    """Question and answer in a report.

    Attributes
    ----------
    id : int
        Unique identifier of the question-answer pair
    question : str
        The text of the question
    question_id : int
        Reference ID of the original question template
    color : str
        Color code for UI display
    answer : str
        The member's answer to the question
    images : list[dict] = []
        List of image attachments in the answer
    html_formatted : bool = False
        Whether the answer contains HTML formatting
    """

    id: int
    question: str
    question_id: int
    color: str
    answer: str
    images: List[Dict[str, Any]] = []
    html_formatted: bool = False


class StandupReport(msgspec.Struct, kw_only=True):
    """A standup report.

    Attributes
    ----------
    id : int
        Unique identifier of the report
    slack_ts : str = None
        Slack timestamp of the report message
    standup_id : int
        ID of the standup this report belongs to
    timestamp : int = None
        Unix timestamp when the report was submitted
    channel : str = None
        Slack channel where the report was posted
    member : ReportMember = None
        The member who submitted the report
    questions : list[ReportQuestion] = []
        List of questions and answers in this report
    """

    id: int
    standup_id: int
    slack_ts: Optional[str] = None
    timestamp: Optional[int] = None
    channel: Optional[str] = None
    member: Optional[ReportMember] = None
    questions: List[ReportQuestion] = []


class ReportAnswerText(msgspec.Struct, kw_only=True):
    """Text answer to a standup question.

    Attributes
    ----------
    text : str
        The answer text content
    """

    text: str


class ReportCreate(msgspec.Struct, kw_only=True):
    """Data for creating a new report.

    Attributes
    ----------
    standup_id : int
        Unique identifier of the standup
    answers : dict[str, dict[str, str]]
        Mapping of question IDs to answer objects containing text
    """

    standup_id: int
    answers: Dict[str, Dict[str, str]]  # Format: {"question_id": {"text": "answer"}}


class StandupUser(msgspec.Struct, kw_only=True):
    """User in a standup.

    Attributes
    ----------
    id : str
        Unique identifier of the user
    username : str
        Slack username of the user
    realname : str
        Full name of the user
    profile_img : str = None
        URL to the user's profile image
    role : str = None
        Role of the user in the team
    email : str = None
        Email address of the user
    deleted : bool = False
        Whether the user has been deleted
    """

    id: str
    username: str
    realname: str
    profile_img: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    deleted: bool = False


class StandupQuestion(msgspec.Struct, kw_only=True):
    """A question in a standup.

    Attributes
    ----------
    id : int
        Unique identifier of the question
    text : str = None
        The text of the question
    color : str
        Color code for UI display
    schedule : str = None
        Schedule for the question
    answer_type : str = "text"
        Type of answer expected
    answer_choices : list = []
        List of possible answer choices
    hasAnswers : bool = True
        Whether the question requires an answer
    is_random : bool = False
        Whether the question is randomly selected
    random_texts : list = []
        List of random text variations
    prefilled_by : int = None
        ID of the question that prefills this one
    text_id : int = None
        Reference ID for the question text
    preconditions : list = []
        List of preconditions for the question
    label : str = None
        Label identifying the question type
    """

    id: int
    color: str
    text: Optional[str] = None
    schedule: Optional[str] = None
    answer_type: str = "text"
    answer_choices: List[str] = []
    hasAnswers: bool = True
    is_random: bool = False
    random_texts: List[str] = []
    prefilled_by: Optional[int] = None
    text_id: Optional[int] = None
    preconditions: List[Any] = []
    label: Optional[str] = None


class Standup(msgspec.Struct, kw_only=True):
    """A standup configuration.

    Attributes
    ----------
    id : int
        Unique identifier of the standup
    name : str
        Name of the standup
    channel : str
        Slack channel for the standup
    time : str
        Time of day when the standup occurs (HH:MM:SS format)
    timezone : str
        Timezone for the standup
    days : list[str]
        Days of the week when the standup occurs
    questions : list[StandupQuestion]
        List of questions to ask
    users : list[StandupUser]
        List of users participating in the standup
    wait_time : int = None
        Time to wait for responses in minutes. -1 indicates no wait time.
    personalised : bool = False
        Whether users can change their personal schedule
    sync_channel_members : bool = False
        Whether to sync with channel membership
    """

    id: int
    name: str
    channel: str
    time: str
    timezone: str
    days: List[str]
    questions: List[StandupQuestion]
    users: List[StandupUser]
    wait_time: Optional[int] = None
    personalised: bool = False
    sync_channel_members: bool = False


class StandupCreate(msgspec.Struct, kw_only=True):
    """Data for creating a new standup.

    Attributes
    ----------
    name : str
        Name of the standup
    channel : str
        Slack channel for the standup
    time : str
        Time of day when the standup occurs (HH:MM:SS format)
    timezone : str
        Timezone for the standup
    days : list[str]
        Days of the week when the standup occurs (3-letter format: Mon, Tue, etc)
    questions : list[dict] = None
        List of questions to ask, each containing a "question" property
    users : list[int]
        List of user IDs to include
    wait_time : int = None
        Time to wait for responses in minutes
    personalised : bool = False
        Whether users can change their personal schedule
    sync_channel_members : bool = False
        Whether to sync with channel membership
    """

    name: str
    channel: str
    time: str
    timezone: str
    days: List[str]
    users: List[int]
    questions: Optional[List[StandupQuestion]] = None
    wait_time: Optional[int] = None
    personalised: bool = False
    sync_channel_members: bool = False


class StandupUpdate(msgspec.Struct, kw_only=True, omit_defaults=True):
    """Data for updating a standup.

    Attributes
    ----------
    name : str = None
        New name for the standup
    channel : str = None
        New Slack channel
    time : str = None
        New time of day (HH:MM:SS format)
    timezone : str = None
        New timezone
    days : list[str] = None
        New days of the week (3-letter format: Mon, Tue, etc)
    wait_time : int = None
        New wait time in minutes
    questions : list[dict] = None
        New list of questions, each containing a "question" property
    users : list[int] = None
        New list of user IDs
    personalised : bool = None
        New personalization setting
    sync_channel_members : bool = None
        New channel sync setting
    """

    name: Optional[str] = None
    channel: Optional[str] = None
    time: Optional[str] = None
    timezone: Optional[str] = None
    days: Optional[List[str]] = None
    wait_time: Optional[int] = None
    questions: Optional[List[dict]] = None
    users: Optional[List[int]] = None
    personalised: Optional[bool] = None
    sync_channel_members: Optional[bool] = None


class Team(msgspec.Struct, kw_only=True):
    """Team information.

    Attributes
    ----------
    id : int
        Unique identifier of the team
    name : str
        Name of the team
    users : list[StandupUser]
        List of users in the team
    """

    id: int
    name: str
    users: List[StandupUser]


class StandupStart(msgspec.Struct, kw_only=True):
    """Data for starting a standup.

    Attributes
    ----------
    users : list[int] = None
        List of user IDs to start the standup for
    emails : list[str] = None
        List of user emails to start the standup for
    """

    users: Optional[List[int]] = None
    emails: Optional[List[str]] = None

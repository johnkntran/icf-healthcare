import datetime
import typing
import enum

from pydantic import BaseModel, Field, model_serializer, UUID4

from encryption import decrypt


class User(BaseModel):
    id: UUID4
    username: str


class Feedback(BaseModel):
    id: UUID4
    user: User
    title: bytes 
    title_nonce: bytes
    body: bytes 
    body_nonce: bytes
    created: datetime.datetime
    updated: datetime.datetime
    
    @model_serializer()
    def serialize_model(self) -> dict:
        return {
            'id': self.id,
            'user': self.user.model_dump(),
            'title': decrypt(self.title, self.title_nonce), # Decrypt title and body
            'body': decrypt(self.body, self.body_nonce), # ... upon JSON rendering
            'created': self.created,
            'updated': self.updated,
        }


class LLMInsight(BaseModel):
    """
    Use this schema as your structured LLM output. This schema represents key metrics that are 
    extracted from a user's feedback for a healthcare EHR system.
    """
    sentiment: typing.Literal['positive', 'neutral', 'negative'] = Field(description="The sentiment of the user's feedback, either: positive, neutral, or negative.")
    key_topics: list[str] = Field(description="A list of 3-5 main topics that were mentioned in the user's feedback.")
    action_required: bool = Field(description="Whether or not there are action items mentioned in the user's feedback. If so, mention these items in the summary field.")
    summary: str = Field(description="A one sentence summary of the user's feedback. Mention any actions items if action items were present in the user's feedback.")
    tokens: int = Field(description='Populate this field as 0 for now. It will be updated by an external process later.')
    latency: float = Field(description='Populate this field as 0 for now. It will be updated by an external process later.')
    feedback_id: str = Field(description='Populate this field as an empty string for now. It will be updated by an external process later.')


class Insight(BaseModel):
    feedback: Feedback
    sentiment: typing.Literal['positive', 'neutral', 'negative']
    key_topics: list[str]
    action_required: bool
    summary: str
    tokens: int
    latency: float


class LLMModel(str, enum.Enum):
    CLAUDE_3_7_SONNET = 'claude-3-7-sonnet'
    GPT_O4_MINI = 'gpt-o4-mini'
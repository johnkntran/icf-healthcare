import datetime

from pydantic import BaseModel, model_serializer, UUID4

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
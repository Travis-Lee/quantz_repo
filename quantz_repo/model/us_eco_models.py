from mongoengine import Document, FloatField, DateTimeField


class UsJoblessInitialClaimItem(Document):
    when = DateTimeField(required=True,  unique=False)
    initial_jobless = FloatField(required=True)

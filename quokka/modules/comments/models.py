# coding: utf-8
import uuid
from quokka.core.db import db
from quokka.core.models.signature import Publishable
from quokka.core.models.content import Content
from quokka.utils.settings import get_setting_value


class BaseComment(object):
    author_name = db.StringField(max_length=255, required=True)
    author_email = db.StringField(max_length=255)
    body = db.StringField(required=True)
    spam = db.BooleanField()
    deleted = db.BooleanField()
    content_format = db.StringField(
        choices=('markdown',),
        default="markdown"
    )

    @property
    def gravatar_email(self):
        if self.created_by:
            return self.created_by.email
        return self.author_email


class Reply(Publishable, BaseComment, db.EmbeddedDocument):
    uid = db.StringField()
    parent = db.StringField()
    replies = db.ListField(db.ReferenceField("Comment"))

    def clean(self):
        if not self.uid:
            self.uid = str(uuid.uuid4())


class Comment(Publishable, BaseComment, db.Document):
    path = db.StringField(max_length=255, required=True)
    #replies = db.ListField(db.EmbeddedDocumentField(Reply))
    replies = db.ListField(db.ReferenceField("self"))
    is_reply = db.BooleanField(default=False)
    content = db.ReferenceField(Content)

    def __unicode__(self):
        return u"{0} - {1}...".format(self.author_name, self.body[:15])

    def clean(self):
        try:
            content = Content.objects.get(long_slug=self.path)
            self.content = content
        except Exception, e:
            raise db.ValidationError("comment path is not a valid content long slug")

    def get_canonical_url(self):
        return "/{0}.{1}".format(
            self.path, get_setting_value('CONTENT_EXTENSION', 'html')
        ) if not self.path.startswith("/") else self.path

    meta = {
        "ordering": ['-created_at'],
        "indexes": ['-created_at', 'path']
    }

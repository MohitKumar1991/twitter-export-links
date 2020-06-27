from api.core import Mixin
from .base import db
from datetime import datetime
from base64 import b64encode, b64decode


class Link(Mixin, db.Model):
    """Person Table."""

    __tablename__ = "link"

    id = db.Column(db.Integer, unique=True, primary_key=True)
    desc = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    parent_link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=True)
    parent_link = db.Column( db.Integer, db.ForeignKey("link.id", ondelete="SET NULL"), nullable=True)
    root_link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=True)
    root_link = db.Column( db.Integer, db.ForeignKey("link.id", ondelete="SET NULL"), nullable=True )
    created_by = db.Column(db.String, nullable=False) #person who is sending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def url_from_username(cls, root_created_by, created_by=None):
        if created_by:
            unique_str = root_created_by + '__' + str(datetime.now()) +  '__' +  created_by
        return b64encode(unique_str.encode('utf-8')).decode('utf-8')


    def __repr__(self):
        return f"<Link {self.id} {self.desc} by {self.created_by}>"

from api.core import Mixin
from .base import db
from .Link import Link

# Note that we use sqlite for our tests, so you can't use Postgres Arrays
class Email(Mixin, db.Model):
    """Email Table."""

    __tablename__ = "email"

    id = db.Column(db.Integer, unique=True, primary_key=True)
    email = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    parent_link_id = db.Column(db.Integer, db.ForeignKey('link.id'),
        nullable=False)
    parent_link = db.Column(
        db.Integer, db.ForeignKey("link.id", ondelete="SET NULL"), nullable=True
    )

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return f"<Email {self.email}>"

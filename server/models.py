from sqlalchemy_serializer import SerializerMixin
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, foreign
from sqlalchemy import and_
from sqlalchemy.ext.declarative import declared_attr
from config import db, bcrypt
import re

# =====================
# Utility
# =====================
def get_utc_now():
    return datetime.now(timezone.utc)

# =====================
# Constants
# =====================
FACT_CHECK_LEVELS = {
    0: "Unverified",
    1: "Misleading",
    2: "Some Inaccuracy",
    3: "Mostly Accurate",
    4: "Verified"
}

# =====================
# Mixins
# =====================
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    def to_dict(self):
        result = super().to_dict() if hasattr(super(), "to_dict") else {}
        result["created_at"] = self.created_at.isoformat() if self.created_at else None
        result["updated_at"] = self.updated_at.isoformat() if self.updated_at else None
        return result

# =====================
# Models
# =====================

class User(db.Model, SerializerMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    submitted_articles = db.relationship('Article', back_populates='submitted_by')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    fact_checks = db.relationship('FactCheck', back_populates='user', passive_deletes=True)

    serialize_rules = (
        '-_password_hash',
        '-submitted_articles.submitted_by',
        '-comments.user',
        '-fact_checks.user',
    )

    @hybrid_property
    def password_hash(self):
        raise Exception("Password hashes can't be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        errors = []

        if not password or not password.strip():
            errors.append("Please enter a password.")
        else:
            if len(password.strip()) < 6:
                errors.append("Password must be at least 6 characters long.")
            if not re.search(r'[a-z]', password):
                errors.append("Include at least one lowercase letter (a–z).")
            if not re.search(r'[A-Z]', password):
                errors.append("Include at least one uppercase letter (A–Z).")
            if not re.search(r'\d', password):
                errors.append("Include at least one number (0–9).")
            if ' ' in password:
                errors.append("Passwords cannot contain spaces.")

            if errors:
                raise ValueError(''.join(errors))

        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))


class Vote(db.Model, SerializerMixin):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    votable_type = db.Column(db.String, nullable=False)  # 'article', 'comment', 'fact_check'
    votable_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Integer, nullable=False)  # 1 or -1
    created_at = db.Column(db.DateTime, default=get_utc_now)

    article_votable = db.relationship(
        "Article",
        back_populates="votes",
        primaryjoin="and_(foreign(Vote.votable_id) == Article.id, Vote.votable_type == 'Article')",
        overlaps="comment_votable,fact_check_votable"
    )

    comment_votable = db.relationship(
        'Comment',
        back_populates='votes',
        primaryjoin="and_(foreign(Vote.votable_id) == Comment.id, Vote.votable_type == 'Comment')",
        overlaps="article_votable,fact_check_votable"
    )

    fact_check_votable = db.relationship(
        'FactCheck',
        back_populates='votes',
        primaryjoin="and_(foreign(Vote.votable_id) == FactCheck.id, Vote.votable_type == 'FactCheck')",
        overlaps="article_votable,comment_votable"
    )

    serialize_rules = (
        '-article_votable.votes',
        '-comment_votable.votes',
        '-fact_check_votable.votes',
    )

    @staticmethod
    def calculate_score(votable_type, votable_id):
        votes = Vote.query.filter_by(votable_type=votable_type, votable_id=votable_id).all()
        return sum(v.value for v in votes)


class Article(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "article"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)

    submitted_by = db.relationship('User', back_populates='submitted_articles')
    comments = db.relationship('Comment', back_populates='article', cascade='all, delete-orphan')
    fact_checks = db.relationship('FactCheck', back_populates='article', cascade='all, delete-orphan')

    votes = db.relationship(
    'Vote',
    primaryjoin=and_(
        foreign(Vote.votable_id) == id,
        Vote.votable_type == 'Article'
    ),
    back_populates='article_votable',
    overlaps="fact_check_votable,comment_votable,votes"
    )

    serialize_rules = (
        '-submitted_by.submitted_articles',
        '-submitted_by.comments',
        '-submitted_by.fact_checks',
        '-comments.article',
        '-comments.user',
        '-fact_checks.article',
        '-fact_checks.user',
        '-votes.article_votable',
    )

    def to_dict(self):
        data = super().to_dict()
        data['fact_checks'] = [fc.to_dict() for fc in self.fact_checks]
        return data

    @property
    def score(self):
        return Vote.calculate_score('article', self.id)


class Comment(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User', back_populates='comments')
    article = db.relationship('Article', back_populates='comments')

    votes = db.relationship(
    'Vote',
    primaryjoin=and_(
        foreign(Vote.votable_id) == id,
        Vote.votable_type == 'Comment'
    ),
    back_populates='comment_votable',
    overlaps="article_votable,fact_check_votable,votes"
    )


    serialize_rules = (
        '-user.comments',
        '-article.comments',
        '-votes.comment_votable',
        '-votes.user',
    )
    
    def to_dict(self):
        data = super().to_dict()
        data['user'] = self.user.to_dict() if self.user else None
        data['article'] = self.article.to_dict() if self.article else None
        data['votes'] = [v.to_dict() for v in self.votes]
        return data

    @property
    def score(self):
        return Vote.calculate_score('comment', self.id)


class FactCheck(db.Model, SerializerMixin):
    __tablename__ = "fact_check"

    id = db.Column(db.Integer, primary_key=True)
    fact_check_level = db.Column(db.Integer, nullable=False, default=0)
    content = db.Column(db.String(2000), nullable=True)
    source = db.Column(db.String(150), nullable=False)
    fact_check_url = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User', back_populates='fact_checks')
    article = db.relationship('Article', back_populates='fact_checks')
    votes = db.relationship(
    'Vote',
    primaryjoin=and_(
        foreign(Vote.votable_id) == id,
        Vote.votable_type == 'FactCheck'
    ),
    back_populates='fact_check_votable',
    overlaps="article_votable,comment_votable,votes"
    )


    serialize_rules = (
        '-user.fact_checks',
        '-article.fact_checks',
        '-votes.factcheck_votable',
        '-votes.user',
    )

    def to_dict(self):
        data = super().to_dict()
        data['fact_check_level_label'] = self.fact_check_level_label
        data['votes'] = [v.to_dict() for v in self.votes]
        return data

    @property
    def fact_check_level_label(self):
        return FACT_CHECK_LEVELS.get(self.fact_check_level, "Unknown")

    @property
    def score(self):
        return Vote.calculate_score('fact_check', self.id)

# Uncomment these when ready to use categories
# class Category(db.Model, SerializerMixin):
#     __tablename__ = "category"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)

# class ArticleCategory(db.Model, SerializerMixin):
#     __tablename__ = "article_category"
#     # Join table between Article and Category
#     pass

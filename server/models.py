from sqlalchemy_serializer import SerializerMixin
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask import jsonify

def get_utc_now():
    return datetime.now(timezone.utc)

# Mixin for automatic timestamps
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    def to_dict(self):
        result = super().to_dict() if hasattr(super(), "to_dict") else {}
        result["created_at"] = self.created_at.isoformat() if self.created_at else None
        result["updated_at"] = self.updated_at.isoformat() if self.updated_at else None
        return result


# =====================
# Fact Check Level Dictionary
# =====================
FACT_CHECK_LEVELS = {
    0: "Unverified",
    1: "Misleading",
    2: "Some Inaccuracy",
    3: "Mostly Accurate",
    4: "Verified"
}

# =====================
# Models
# =====================

# Article Model
class Article(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "article"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)

    # Relationships
    submitted_by = db.relationship('User', back_populates='submitted_articles')
    comments = db.relationship('Comment', back_populates='article', cascade='all, delete-orphan')
    fact_checks = db.relationship('FactCheck', back_populates='article', cascade='all, delete-orphan')

    serialize_rules = (
        '-submitted_by.submitted_articles',
        '-submitted_by.comments',
        '-submitted_by.fact_checks',
        '-comments.article',
        '-comments.user',
        '-fact_checks.article',
        '-fact_checks.user',
    )

# User Model
class User(db.Model, SerializerMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    submitted_articles = db.relationship('Article', back_populates='submitted_by')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    fact_checks = db.relationship('FactCheck', back_populates='user', passive_deletes=True)

    serialize_rules = (
        '-_password_hash',
        '-submitted_articles.submitted_by',
        '-comments.user',
        '-fact_checks.user',
    )

    # Password Handling
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

        # If all checks pass, hash the password
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

# Comment Model
class Comment(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='comments')
    article = db.relationship('Article', back_populates='comments')

    serialize_rules = (
        '-user.comments',
        '-article.comments',
    )

# FactCheck Model
class FactCheck(db.Model, SerializerMixin):
    __tablename__ = "fact_check"

    id = db.Column(db.Integer, primary_key=True)
    fact_check_level = db.Column(db.Integer, nullable=False, default=0)  # Fact check level (Unverified, etc.)
    content = db.Column(db.String(2000), nullable=True)
    source = db.Column(db.String(150), nullable=False)
    fact_check_url = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='fact_checks')
    article = db.relationship('Article', back_populates='fact_checks')
    #votes = db.relationship('FactCheckVote', back_populates='fact_check', cascade='all, delete-orphan')

    serialize_rules = (
        '-user.fact_checks',
        '-article.fact_checks',
        #'-votes.fact_check',  # Exclude fact check votes from serialization
    )

    @property
    def fact_check_level_label(self):
        return FACT_CHECK_LEVELS.get(self.fact_check_level, "Unknown")

# Uncomment these when ready to use categories
# class Category(db.Model, SerializerMixin):
#     __tablename__ = "category"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)

# class ArticleCategory(db.Model, SerializerMixin):
#     __tablename__ = "article_category"
#     # Join table between Article and Category
#     pass

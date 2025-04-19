from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash

def get_utc_now():
    return datetime.now(timezone.utc)

# Mixin for automatic timestamps
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    def to_dict(self):
        """Convert model instance to dictionary with custom datetime formatting."""
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        # Custom datetime formatting
        if data.get('created_at'):
            data['created_at'] = data['created_at'].strftime('%Y-%m-%d %H:%M:%S')  # Example: 2025-04-18 15:30:00
        if data.get('updated_at'):
            data['updated_at'] = data['updated_at'].strftime('%Y-%m-%d %H:%M:%S')  # Example: 2025-04-18 15:30:00
        return data

# =====================
# Models
# =====================

# Article Model 
class Article(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "article"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='articles')
    comments = db.relationship('Comment', back_populates='article', cascade='all, delete-orphan')
    fact_checks = db.relationship('FactCheck', back_populates='article', cascade='all, delete-orphan')

    serialize_rules = ('-user.articles', '-comments.article', '-fact_checks.article')


# User Model
class User(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)

    # Relationships
    articles = db.relationship('Article', back_populates='user')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    fact_checks = db.relationship('FactCheck', back_populates='user', passive_deletes=True)

    serialize_rules = ('-_password_hash', '-articles.user', '-comments.user', '-fact_checks.user')

    # Password Handling
    @hybrid_property
    def password_hash(self):
        raise Exception("Password hashes can't be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))


# Comment Model
class Comment(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='comments')
    article = db.relationship('Article', back_populates='comments')

    serialize_rules = ('-user.comments', '-article.comments')


# FactCheck Model
class FactCheck(db.Model, SerializerMixin):
    __tablename__ = "fact_check"

    id = db.Column(db.Integer, primary_key=True)
    verified_status = db.Column(db.Boolean, nullable=False)
    source = db.Column(db.String, nullable=False)
    fact_check_url = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='fact_checks')
    article = db.relationship('Article', back_populates='fact_checks')

    serialize_rules = ('-user.fact_checks', '-article.fact_checks')




# Uncomment these when ready to use categories
# class Category(db.Model, SerializerMixin):
#     __tablename__ = "category"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)

# class ArticleCategory(db.Model, SerializerMixin):
#     __tablename__ = "article_category"
#     # Join table between Article and Category
#     pass

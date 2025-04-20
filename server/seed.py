#!/usr/bin/env python3

# Standard library imports
from random import randint, choice as rc

# Remote library imports
from faker import Faker

# Local imports
from app import app
from models import db
from datetime import datetime
from app import db  
from models import User, Article, Comment, FactCheck  # Import your models here

# Create some sample users
def create_users():
    user1 = User(username="user1", email="user1@example.com")
    user1._password_hash = "Password1"  # Use the setter to hash the password
    
    user2 = User(username="user2", email="user2@example.com")
    user2._password_hash = "Password2"  # Use the setter to hash the password

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    return user1, user2

# Create some sample articles
def create_articles(user1, user2):
    article1 = Article(
        title="First Article by User 1",  # Add title here
        url="https://example.com/article1",  # Add a URL here
        submitted_by_id=user1.id  # Link to user1
    )
    article2 = Article(
        title="Second Article by User 2",  # Add title here
        url="https://example.com/article2",  # Add a URL here
        submitted_by_id=user2.id  # Link to user2
    )

    db.session.add(article1)
    db.session.add(article2)
    db.session.commit()

    return article1, article2

# Create some sample comments
def create_comments(user1, user2, article1, article2):
    comment1 = Comment(content="Great article!", user_id=user1.id, article_id=article1.id)
    comment2 = Comment(content="I disagree with this article.", user_id=user2.id, article_id=article2.id)

    db.session.add(comment1)
    db.session.add(comment2)
    db.session.commit()

# Create some sample fact checks
def create_fact_checks(user1, article1, article2):
    fact_check1 = FactCheck(verified_status=True, source="https://example.com", fact_check_url="https://example.com/fact_check_1", user_id=user1.id, article_id=article1.id)
    fact_check2 = FactCheck(verified_status=False, source="https://example.com", fact_check_url="https://example.com/fact_check_2", user_id=user1.id, article_id=article2.id)

    db.session.add(fact_check1)
    db.session.add(fact_check2)
    db.session.commit()

# Main function to run the seed script
def run_seed():
    with app.app_context():  # Make sure you're within the app context
        print("Starting seed...")

        # Drop all tables if they exist before creating new ones
        db.drop_all()

        # Initialize the database and create tables
        db.create_all()

        # Create users
        user1, user2 = create_users()

        # Create articles
        article1, article2 = create_articles(user1, user2)

        # Create comments
        create_comments(user1, user2, article1, article2)

        # Create fact checks
        create_fact_checks(user1, article1, article2)

        print("Database seeded successfully!")

# Run the seed function
if __name__ == "__main__":
    run_seed()

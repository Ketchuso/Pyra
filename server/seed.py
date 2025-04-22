#!/usr/bin/env python3

# Standard library imports
from random import randint, choice as rc

# Remote library imports
from faker import Faker

# Local imports
from app import app
from models import db, User, Article, Comment, FactCheck
from datetime import datetime

fake = Faker()

# Create sample users
def create_users():
    user1 = User(username="user1", email="user1@example.com")
    user1.password_hash = "Password1"  # This uses the secure setter

    user2 = User(username="user2", email="user2@example.com")
    user2.password_hash = "Password2"

    db.session.add_all([user1, user2])
    db.session.commit()

    return user1, user2

# Create sample articles
def create_articles(user1, user2):
    article1 = Article(
        title="Divided Supreme Court finds some deadline flexibility for immigrants who agree to leave US",
        url="https://apnews.com/article/supreme-court-immigration-deadlines-6cba58871ea6dfac7325326ff1f8d5b8",
        image_url="https://dims.apnews.com/dims4/default/d59cb8f/2147483647/strip/true/crop/4500x2998+0+1/resize/980x653!/format/webp/quality/90/?url=https%3A%2F%2Fassets.apnews.com%2Fcf%2F79%2F5bf6b2192813ed8b3cb5d90d212f%2F3d9d0d587d6343848e759ae90b09b2d3",
        submitted_by_id=user1.id
    )
    article2 = Article(
        title="What to know about the severe storms and flash flooding hitting parts of the US",
        url="https://apnews.com/article/severe-weather-flooding-tornado-5031aa5a5ebeec0e50c1b753acd81bf0",
        image_url="https://dims.apnews.com/dims4/default/43516db/2147483647/strip/true/crop/4032x3024+0+0/resize/1440x1080!/format/webp/quality/90/?url=https%3A%2F%2Fassets.apnews.com%2Fc9%2Ffe%2F9200fb30d53b0e66f31fc6f76d1e%2Fbc66fb898784405f97cecbcd2d6e5c18",
        submitted_by_id=user2.id
    )

    db.session.add_all([article1, article2])
    db.session.commit()

    return article1, article2

# Create sample comments
def create_comments(user1, user2, article1, article2):
    comment1 = Comment(content="Great article!", user_id=user1.id, article_id=article1.id)
    comment2 = Comment(content="I disagree with this article.", user_id=user2.id, article_id=article2.id)

    db.session.add_all([comment1, comment2])
    db.session.commit()

# Create sample fact checks
def create_fact_checks(user1, article1, article2):
    fact_check1 = FactCheck(
        fact_check_level=4,  # Verified
        content="This article has been verified with multiple sources.",
        source="https://example.com/source1",
        fact_check_url="https://example.com/fact_check_1",
        user_id=user1.id,
        article_id=article1.id
    )
    fact_check2 = FactCheck(
        fact_check_level=1,  # Misleading
        content="This article contains misleading statements.",
        source="https://example.com/source2",
        fact_check_url="https://example.com/fact_check_2",
        user_id=user1.id,
        article_id=article2.id
    )

    db.session.add_all([fact_check1, fact_check2])
    db.session.commit()

# Main function to run the seed script
def run_seed():
    with app.app_context():
        print("Seeding database...")

        # Drop all tables
        db.drop_all()

        # Create all tables
        db.create_all()

        # Populate with data
        user1, user2 = create_users()
        article1, article2 = create_articles(user1, user2)
        create_comments(user1, user2, article1, article2)
        create_fact_checks(user1, article1, article2)

        print("Database seeded successfully!")

# Run the seed function
if __name__ == "__main__":
    run_seed()

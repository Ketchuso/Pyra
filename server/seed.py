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
    users = []
    for i in range(10):
        user = User(
            username=fake.user_name(),
            email=fake.email()
        )
        user.password_hash = f"Password{i}"  # Uses the secure setter
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    return users

# Create sample articles
def create_articles(users):
    lorem_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )
    articles = [
        Article(
            title=lorem_text,
            url="https://www.reuters.com/fact-check/ai-images-flooded-disney-world-spread-online-2024-10-15/",
            image_url="https://www.reuters.com/resizer/v2/RBHHM67HZBDHDGWNKJIIYWWZC4.jpg?auth=0326ec4968945626223b259fbc5e0faba9e7d86b7bd6b51e4a71f6a5958291a9&width=720&quality=80",
            submitted_by_id=rc(users).id
        ),
        Article(
            title=lorem_text,
            url="https://www.reuters.com/fact-check/al-capone-soup-kitchen-image-is-ai-generated-2024-07-05/",
            image_url="https://www.reuters.com/resizer/v2/MVXIY6Y3Y5ATDL2LM5KG2WZLAU.jpg?auth=d80c4d2b2b0f1ec860a1689ae1e51673395dfd6ce3c47a76fd0d08fde5c1b445&width=720&quality=80",
            submitted_by_id=rc(users).id
        ),
        Article(
            title=lorem_text,
            url="https://www.reuters.com/fact-check/picture-claudia-sheinbaum-holding-menorah-was-digitally-altered-2024-06-21/",
            image_url="https://www.reuters.com/resizer/v2/JUPGQHR5KNB7VG2BPAVVMJE5K4.jpg?auth=0bd5367d98dca0ccac19e50df7b000e20d2d8e289e0be357d974ffc070e9d3a3&width=640&quality=80",
            submitted_by_id=rc(users).id
        ),
        Article(
            title=lorem_text,
            url="https://www.reuters.com/fact-check/plane-reflection-not-proof-image-manipulation-michigan-harris-rally-2024-08-22/",
            image_url="https://www.reuters.com/resizer/v2/ZEPPHZCW3FEYHAHSIJINV7WSUA.jpg?auth=64f048d2d0373ba172e0c4650bc8a78c6bc9e061f7bd12ac81123825828daf74&width=720&quality=80",
            submitted_by_id=rc(users).id
        ),
        Article(
            title=lorem_text,
            url="https://time.com/7204123/time-top-10-photos-2024/",
            image_url="https://api.time.com/wp-content/uploads/2024/12/top-10-photos-2024-01.jpg?quality=75&w=828",
            submitted_by_id=rc(users).id
        ),
        Article(
            title=lorem_text,
            url="https://apnews.com/article/nasa-water-moon-6",
            image_url="https://example.com/image6.jpg",
            submitted_by_id=rc(users).id
        ),
        Article(
            title=lorem_text,
            url="https://apnews.com/article/ai-cancer-diagnosis-7",
            image_url="https://example.com/image7.jpg",
            submitted_by_id=rc(users).id
        ),
        # Post with no comments or fact checks
        Article(
            title="Post with no comments or fact checks",
            url="https://snopes.com/fact-check/example-no-checks-or-comments",
            image_url="https://example.com/no-comments-or-checks.jpg",
            submitted_by_id=rc(users).id
        )
    ]

    db.session.add_all(articles)
    db.session.commit()
    return articles

# Create sample comments
def create_comments(users, articles):
    lorem_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )
    comments = []
    for _ in range(30):
        comment = Comment(
            content=lorem_text,
            user_id=rc(users).id,
            article_id=rc(articles[:-1]).id  # Exclude the last article
        )
        comments.append(comment)

    db.session.add_all(comments)
    db.session.commit()

# Create sample fact checks
def create_fact_checks(users, articles):
    lorem_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )
    fact_levels = [1, 2, 3, 4, 5]
    fact_checks = []

    for article in articles[:-1]:  # Exclude the last article
        for _ in range(7):
            fact_checks.append(
                FactCheck(
                    fact_check_level=rc(fact_levels),
                    content=lorem_text,
                    source=fake.url(),
                    fact_check_url=fake.url(),
                    user_id=rc(users).id,
                    article_id=article.id
                )
            )

    db.session.add_all(fact_checks)
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
        users = create_users()
        articles = create_articles(users)
        create_comments(users, articles)
        create_fact_checks(users, articles)

        print("Database seeded successfully!")

# Run the seed function
if __name__ == "__main__":
    run_seed()

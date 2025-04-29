#!/usr/bin/env python3

# Standard library imports
from random import randint, choice as rc

# Remote library imports
from faker import Faker

# Local imports
from app import app
from models import db, User, Article, Comment, FactCheck, Vote
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
        # Add other articles here...
    ]
    
    # Add more articles if needed
    for _ in range(5):  # Adjust this number to create more articles
        articles.append(
            Article(
                title=lorem_text,
                url=f"https://example.com/{fake.uuid4()}/",
                image_url=f"https://example.com/{fake.uuid4()}.jpg",
                submitted_by_id=rc(users).id
            )
        )

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
    
    if len(articles) > 1:  # Ensure we have more than one article
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
            fact_check = FactCheck(
                fact_check_level=rc(fact_levels),
                content=lorem_text,
                source=fake.url(),
                fact_check_url=fake.url(),
                user_id=rc(users).id,
                article_id=article.id
            )
            fact_checks.append(fact_check)

            # Add random upvotes/downvotes for each fact check
            add_votes_for_fact_check(fact_check)

    db.session.add_all(fact_checks)
    db.session.commit()

def add_votes_for_fact_check(fact_check):
    # Ensure fact_check is added to the session before using its ID
    db.session.add(fact_check)
    db.session.flush()  # This will flush the fact_check object to the database and assign it an ID

    # Random number of upvotes and downvotes
    num_upvotes = randint(5, 15)  # Upvotes between 5 and 15
    num_downvotes = randint(0, 5)  # Downvotes between 0 and 5
    
    # Create upvotes
    for _ in range(num_upvotes):
        vote = Vote(
            votable_id=fact_check.id, 
            votable_type='FactCheck', 
            value=1, 
            user_id=rc([user.id for user in User.query.all()])
        )
        db.session.add(vote)

    # Create downvotes
    for _ in range(num_downvotes):
        vote = Vote(
            votable_id=fact_check.id, 
            votable_type='FactCheck', 
            value=-1, 
            user_id=rc([user.id for user in User.query.all()])
        )
        db.session.add(vote)

    db.session.commit()  # Commit all the votes


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

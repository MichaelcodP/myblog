# MyBlog Project

A Django-based blog platform with premium content features, built with Django REST Framework and Stripe integration.

## Features

- User authentication with JWT tokens
- Blog post creation and management
- Premium content with Stripe payments
- Comment system with spam protection
- Like/Unlike functionality
- Safe for work content filtering
- API documentation with Swagger/ReDoc

## Tech Stack

- Python 3.13.7
- Django 5.2.6
- Django REST Framework
- PostgreSQL
- Redis (for caching)
- Celery (for async tasks)
- Stripe (for payments)
- JWT Authentication
- drf-yasg (for API documentation)

## Prerequisites

- Python 3.13+
- PostgreSQL
- Redis
- Stripe account

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourname/myblog_project.git
cd myblog_project
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
"""
Pytest Configuration and Test Fixtures (§81).
"""

import pytest
import os

# Configure test environment
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "true"


@pytest.fixture
def sample_parsed_cv():
    """Sample parsed CV data fixture."""
    return {
        "contact_info": {
            "name": "Alex Mercer",
            "email": "alex.mercer@example.com",
            "phone": "+1 (555) 019-2834",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/alexmercer",
            "github": "github.com/alexmercer",
        },
        "summary": "Staff Backend Engineer with 8+ years designing high-throughput distributed systems, event-driven architectures, and microservices in Python and Go.",
        "skills": [
            "Python", "FastAPI", "Go", "Docker", "PostgreSQL",
            "Redis", "Kafka", "REST APIs", "CI/CD", "Linux", "Git"
        ],
        "experience": [
            {
                "job_title": "Senior Backend Engineer",
                "company": "CloudScale Systems",
                "location": "San Francisco, CA",
                "start_date": "2021-03",
                "end_date": "Present",
                "is_current": True,
                "description": "Architected low-latency microservices handling 45k requests/second.",
                "bullets": [
                    "Engineered distributed event-processing pipeline in Python and Kafka, reducing latency by 42%.",
                    "Scaled PostgreSQL database cluster supporting 12 million daily active transactions.",
                    "Mentored team of 6 engineers and instituted automated pytest CI/CD pipelines.",
                ],
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Kafka", "Docker"],
            },
            {
                "job_title": "Software Engineer",
                "company": "DataVibe Inc",
                "location": "Seattle, WA",
                "start_date": "2018-06",
                "end_date": "2021-02",
                "is_current": False,
                "description": "Developed RESTful APIs and database schemas.",
                "bullets": [
                    "Built 14 internal REST APIs using FastAPI and Redis caching layer.",
                    "Containerized monolithic services into Docker containers.",
                ],
                "technologies": ["Python", "Redis", "Docker", "Git"],
            },
        ],
        "education": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "University of Washington",
                "graduation_year": "2018",
            }
        ],
        "projects": [
            {
                "name": "AsyncQuery",
                "description": "Open-source asynchronous database connection pooler with 1.2k GitHub stars.",
                "technologies": ["Python", "AsyncIO", "PostgreSQL"],
            }
        ],
    }


@pytest.fixture
def sample_parsed_jd():
    """Sample parsed Job Description data fixture."""
    return {
        "job_title": "Staff Backend Engineer",
        "company": "Stripe",
        "seniority": "Staff",
        "department": "Core Infrastructure",
        "requirements": [
            {
                "name": "Python",
                "category": "programming_language",
                "priority": "must_have",
                "years": 5,
            },
            {
                "name": "Distributed Systems",
                "category": "architecture",
                "priority": "must_have",
            },
            {
                "name": "PostgreSQL",
                "category": "database",
                "priority": "must_have",
            },
            {
                "name": "Kafka",
                "category": "messaging",
                "priority": "must_have",
            },
            {
                "name": "Kubernetes",
                "category": "devops",
                "priority": "preferred",
            },
            {
                "name": "GraphQL",
                "category": "api",
                "priority": "bonus",
            },
        ],
    }

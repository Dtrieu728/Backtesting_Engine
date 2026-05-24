import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import init_db

@pytest.fixture(autouse=True, scope="session")
def setup_database():
    """Create tables before any tests run"""
    init_db()
    yield
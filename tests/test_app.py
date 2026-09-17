import pytest
# pytest-mock is automatically imported
from app import app


@pytest.fixture
def mock_db(mocker):
    """Mock database connection"""
    mock = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    # app.py uses sqlite3: execute() returns a cursor, then fetchall() returns rows
    mock_cursor.fetchall.return_value = [
        {
            "id": 1,
            "name": "Test Shirt",
            "price": 29.99,
            "category": "shirts",
            "image_url": "sample0.jpg",
            "description": "A test shirt",
            "stock": 10,
        }
    ]
    mock.execute.return_value = mock_cursor
    mocker.patch("app.get_db", return_value=mock)
    return mock


@pytest.fixture
def client(mock_db):
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client, mock_db):
    """Test that home page loads successfully"""
    rv = client.get("/")
    assert rv.status_code == 200
    # Verify database was queried for products
    mock_db.execute.assert_any_call("SELECT * FROM products ORDER BY id", ())

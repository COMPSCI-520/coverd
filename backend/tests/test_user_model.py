from models.user import User


def test_user_from_mongo_maps_fields():
    mongo_doc = {
        "_id": "user-1",
        "email": "student@coverd.dev",
        "hashed_password": "hashed-password",
        "role": "student",
        "full_name": "Alex Student",
        "is_international": True,
    }

    result = User.from_mongo(mongo_doc)

    assert result.id == "user-1"
    assert result.email == "student@coverd.dev"
    assert result.hashed_password == "hashed-password"
    assert result.role == "student"
    assert result.full_name == "Alex Student"
    assert result.is_international is True


def test_user_can_be_created_for_manager():
    user = User(
        id="manager-1",
        email="manager@coverd.dev",
        hashed_password="hashed-password",
        role="manager",
        full_name="Jordan Manager",
        is_international=False,
    )

    assert user.role == "manager"
    assert user.full_name == "Jordan Manager"
    assert user.is_international is False
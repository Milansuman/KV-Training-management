import pytest


def test_create_topic_returns_topic(client) -> None:
    response = client.post(
        "/topics",
        json={
            "title": "Python Basics"
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Python Basics"
    assert response.json()["id"] is not None


def test_create_topic_with_empty_title_creates_topic(client) -> None:
    response = client.post(
        "/topics",
        json={
            "title": ""
        }
    )

    # API allows empty titles
    assert response.status_code == 200
    assert response.json()["title"] == ""


def test_get_topics_returns_list(client) -> None:
    client.post(
        "/topics",
        json={"title": "Topic 1"}
    )
    client.post(
        "/topics",
        json={"title": "Topic 2"}
    )

    response = client.get("/topics")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2


def test_get_topics_returns_empty_list_initially(client) -> None:
    response = client.get("/topics")

    assert response.status_code == 200
    assert response.json() == []


def test_get_topics_returns_sorted_topics(client) -> None:
    client.post("/topics", json={"title": "Zebra"})
    client.post("/topics", json={"title": "Apple"})
    client.post("/topics", json={"title": "Mango"})

    response = client.get("/topics")

    titles = [t["title"] for t in response.json()]
    assert titles == ["Apple", "Mango", "Zebra"]


def test_get_topic_by_id_returns_topic(client) -> None:
    create_response = client.post(
        "/topics",
        json={"title": "Web Development"}
    )
    topic_id = create_response.json()["id"]

    response = client.get(f"/topics/{topic_id}")

    assert response.status_code == 200
    assert response.json()["id"] == topic_id
    assert response.json()["title"] == "Web Development"


def test_get_topic_by_id_returns_404_for_nonexistent_topic(client) -> None:
    response = client.get("/topics/999")

    assert response.status_code == 404


def test_get_topic_by_id_returns_404_for_deleted_topic(client) -> None:
    create_response = client.post(
        "/topics",
        json={"title": "Topic to Delete"}
    )
    topic_id = create_response.json()["id"]

    client.delete(f"/topics/{topic_id}")

    response = client.get(f"/topics/{topic_id}")
    assert response.status_code == 404


def test_update_topic_modifies_title(client) -> None:
    create_response = client.post(
        "/topics",
        json={"title": "Old Title"}
    )
    topic_id = create_response.json()["id"]

    response = client.patch(
        f"/topics/{topic_id}",
        json={"title": "New Title"}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New Title"
    assert response.json()["id"] == topic_id


def test_update_topic_persists_changes(client) -> None:
    create_response = client.post(
        "/topics",
        json={"title": "Original"}
    )
    topic_id = create_response.json()["id"]

    client.patch(
        f"/topics/{topic_id}",
        json={"title": "Modified"}
    )

    response = client.get(f"/topics/{topic_id}")
    assert response.json()["title"] == "Modified"


def test_update_topic_returns_404_for_nonexistent_topic(client) -> None:
    response = client.patch(
        "/topics/999",
        json={"title": "New Title"}
    )

    assert response.status_code == 404


def test_update_topic_returns_404_for_deleted_topic(client) -> None:
    create_response = client.post(
        "/topics",
        json={"title": "Topic to Delete"}
    )
    topic_id = create_response.json()["id"]

    client.delete(f"/topics/{topic_id}")

    response = client.patch(
        f"/topics/{topic_id}",
        json={"title": "Updated"}
    )

    assert response.status_code == 404


def test_delete_topic_removes_topic(client) -> None:
    create_response = client.post(
        "/topics",
        json={"title": "Topic to Delete"}
    )
    topic_id = create_response.json()["id"]

    response = client.delete(f"/topics/{topic_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Topic deleted successfully"


def test_delete_topic_makes_topic_unavailable(client) -> None:
    create_response = client.post(
        "/topics",
        json={"title": "Topic"}
    )
    topic_id = create_response.json()["id"]

    client.delete(f"/topics/{topic_id}")

    response = client.get(f"/topics/{topic_id}")
    assert response.status_code == 404


def test_delete_topic_returns_404_for_nonexistent_topic(client) -> None:
    response = client.delete("/topics/999")

    assert response.status_code == 404


def test_delete_topic_returns_404_when_deleted_twice(client) -> None:
    create_response = client.post(
        "/topics",
        json={"title": "Topic"}
    )
    topic_id = create_response.json()["id"]

    client.delete(f"/topics/{topic_id}")

    response = client.delete(f"/topics/{topic_id}")
    assert response.status_code == 404


def test_multiple_topics_operations_work_correctly(client) -> None:
    # Create 3 topics
    t1 = client.post("/topics", json={"title": "Python"}).json()
    t2 = client.post("/topics", json={"title": "JavaScript"}).json()
    t3 = client.post("/topics", json={"title": "Go"}).json()

    # Get all topics
    all_topics = client.get("/topics").json()
    assert len(all_topics) == 3

    # Update one
    updated = client.patch(
        f"/topics/{t1['id']}",
        json={"title": "Python Advanced"}
    ).json()
    assert updated["title"] == "Python Advanced"

    # Delete one
    client.delete(f"/topics/{t2['id']}")

    # Get all topics - should have 2
    remaining = client.get("/topics").json()
    assert len(remaining) == 2

    # Verify correct topics remain
    titles = {t["title"] for t in remaining}
    assert "Python Advanced" in titles
    assert "Go" in titles
    assert "JavaScript" not in titles

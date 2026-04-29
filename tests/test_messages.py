def test_get_messages_empty(client):
    response = client.get("/messages/user1/user2")

    assert response.status_code == 200
    assert response.json() == []
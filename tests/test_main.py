from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def teardown_module(module):
    client.close()


def test_health_endpoint():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_contact_endpoint_accepts_message():
    response = client.post(
        '/api/contact',
        json={
            'name': 'Paras',
            'email': 'paras@example.com',
            'message': 'Hello from the test suite.'
        }
    )
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_contact_endpoint_uses_email_sender(monkeypatch):
    called = {}

    def fake_send_email(name, email, message):
        called['payload'] = (name, email, message)
        return True

    monkeypatch.setattr(main, 'send_contact_email', fake_send_email)

    response = client.post(
        '/api/contact',
        json={
            'name': 'Paras',
            'email': 'paras@example.com',
            'message': 'Hello from the test suite.'
        }
    )

    assert response.status_code == 200
    assert called['payload'] == ('Paras', 'paras@example.com', 'Hello from the test suite.')
    assert response.json()['email_sent'] is True


def test_contact_message_is_saved():
    response = client.post(
        '/api/contact',
        json={
            'name': 'Data',
            'email': 'data@example.com',
            'message': 'Save this message.'
        }
    )

    assert response.status_code == 200
    assert response.json()['success'] is True
    assert response.json()['message_id'] > 0

    list_response = client.get('/api/messages')
    assert list_response.status_code == 200
    messages = list_response.json()
    assert any(msg['email'] == 'data@example.com' and msg['message'] == 'Save this message.' for msg in messages)

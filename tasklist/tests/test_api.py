# pylint: disable=missing-module-docstring,missing-function-docstring
import os.path

from fastapi.testclient import TestClient

from utils import utils

from tasklist.main import app

client = TestClient(app)

app.dependency_overrides[utils.get_config_filename] = \
    utils.get_config_test_filename


def setup_database():
    scripts_dir = os.path.join(
        os.path.dirname(__file__),
        '..',
        'database',
        'migrations',
    )
    config_file_name = utils.get_config_test_filename()
    secrets_file_name = utils.get_admin_secrets_filename()
    utils.run_all_scripts(scripts_dir, config_file_name, secrets_file_name)


def test_read_main_returns_not_found():
    setup_database()
    response = client.get('/')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_tasks_with_no_task():
    setup_database()
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {}


def test_create_and_read_some_tasks():
    setup_database()

    # Create a user
    user = {"name": "giovanna"}
    response = client.post("/user", json=user)
    assert response.status_code == 200
    user_uuid = response.json()

    # Create a list of tasks
    tasks = [
        {
            "description": "foo",
            "completed": False,
            "user_uuid": user_uuid,
        },
        {
            "description": "bar",
            "completed": True,
            "user_uuid": user_uuid,
        },
        {
            "description": "baz",
            "user_uuid": user_uuid,
        },
        {
            "completed": True,
            "user_uuid": user_uuid,
        },
    ]
    expected_responses = [
        {
            'description': 'foo',
            'completed': False,
            "user_uuid": user_uuid,
        },
        {
            'description': 'bar',
            'completed': True,
            "user_uuid": user_uuid,
        },
        {
            'description': 'baz',
            'completed': False,
            "user_uuid": user_uuid,
        },
        {
            'description': 'no description',
            'completed': True,
            "user_uuid": user_uuid,
        },
        {
            'description': 'no description',
            'completed': False,
            "user_uuid": user_uuid,
        },
    ]

    # Insert some tasks and check that all succeeded.
    uuids = []
    for task in tasks:
        response = client.post("/task", json=task)
        assert response.status_code == 200
        uuids.append(response.json())

    # Read the complete list of tasks.
    def get_expected_responses_with_uuid(completed=None):
        return {
            uuid_: response
            for uuid_, response in zip(uuids, expected_responses)
            if completed is None or response['completed'] == completed
        }

    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == get_expected_responses_with_uuid()

    # Read only completed tasks.
    for completed in [False, True]:
        response = client.get(f'/task?completed={str(completed)}')
        assert response.status_code == 200
        assert response.json() == get_expected_responses_with_uuid(completed)

    # Delete all tasks.
    for uuid_ in uuids:
        response = client.delete(f'/task/{uuid_}')
        assert response.status_code == 200

    # Check whether there are no more tasks.
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {}


def test_substitute_task():
    setup_database()

    # Create a user
    user = {"name": "giovanna"}
    response = client.post("/user", json=user)
    assert response.status_code == 200
    user_uuid = response.json()

    # Create a task.
    task = {'description': 'foo', 'completed': False, "user_uuid": user_uuid}
    response = client.post('/task', json=task)
    assert response.status_code == 200
    uuid_ = response.json()

    # Replace the task.
    new_task = {'description': 'bar', 'completed': True, "user_uuid": user_uuid}
    response = client.put(f'/task/{uuid_}', json=new_task)
    assert response.status_code == 200

    # Check whether the task was replaced.
    response = client.get(f'/task/{uuid_}')
    assert response.status_code == 200
    assert response.json() == new_task

    # Delete the task.
    response = client.delete(f'/task/{uuid_}')
    assert response.status_code == 200


def test_alter_task():
    setup_database()

    # Create a user
    user = {"name": "giovanna"}
    response = client.post("/user", json=user)
    assert response.status_code == 200
    user_uuid = response.json()

    # Create a second user
    user = {"name": "mayra"}
    response = client.post("/user", json=user)
    assert response.status_code == 200
    user_uuid2 = response.json()

    # Create a task.
    task = {'description': 'foo', 'completed': False, "user_uuid": user_uuid}}
    response = client.post('/task', json=task)
    assert response.status_code == 200
    uuid_ = response.json()

    # Replace the task.
    new_task_partial = {'completed': True, "user_uuid": user_uuid2}
    response = client.patch(f'/task/{uuid_}', json=new_task_partial)
    assert response.status_code == 200

    # Check whether the task was altered.
    response = client.get(f'/task/{uuid_}')
    assert response.status_code == 200
    assert response.json() == {**task, **new_task_partial}

    # Delete the task.
    response = client.delete(f'/task/{uuid_}')
    assert response.status_code == 200


def test_read_invalid_task():
    setup_database()

    response = client.get('/task/invalid_uuid')
    assert response.status_code == 422


def test_read_nonexistant_task():
    setup_database()

    response = client.get('/task/3668e9c9-df18-4ce2-9bb2-82f907cf110c')
    assert response.status_code == 404


def test_delete_invalid_task():
    setup_database()

    response = client.delete('/task/invalid_uuid')
    assert response.status_code == 422


def test_delete_nonexistant_task():
    setup_database()

    response = client.delete('/task/3668e9c9-df18-4ce2-9bb2-82f907cf110c')
    assert response.status_code == 404


def test_delete_all_tasks():
    setup_database()

    # Create a user
    user = {"name": "giovanna"}
    response = client.post("/user", json=user)
    assert response.status_code == 200
    user_uuid = response.json()

    # Create a task.
    task = {'description': 'foo', 'completed': False, "user_uuid": user_uuid}
    response = client.post('/task', json=task)
    assert response.status_code == 200
    uuid_ = response.json()

    # Check whether the task was inserted.
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {uuid_: task}

    # Delete all tasks.
    response = client.delete('/task')
    assert response.status_code == 200

    # Check whether all tasks have been removed.
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {}


#user tests

def test_read_users_with_no_user():
    setup_database()
    response = client.get('/user')
    assert response.status_code == 200
    assert response.json() == {}


def test_create_and_read_some_users():
    setup_database()
    users = [
        {
            "name": "giovanna"
        },
        {
            "name": "mayra"
        }
    ]
    expected_responses = [
        {
            "name": "giovanna"
        },
        {
            "name": "mayra"
        }
    ]

    # Insert some users and check that all succeeded.
    uuids = []
    for user in users:
        response = client.post("/user", json=user)
        assert response.status_code == 200
        uuids.append(response.json())

    # Read the complete list of users.
    def get_expected_responses_user_with_uuid():
        return {
            uuid_: response
            for uuid_, response in zip(uuids, expected_responses)
        }

    response = client.get('/user')
    assert response.status_code == 200
    assert response.json() == get_expected_responses_user_with_uuid()

    # Delete all users.
    for uuid_ in uuids:
        response = client.delete(f'/user/{uuid_}')
        assert response.status_code == 200

    # Check whether there are no more tasks.
    response = client.get('/user')
    assert response.status_code == 200
    assert response.json() == {}


def test_substitute_user():
    setup_database()

    # Create a user.
    user = {'name': 'giovanna'}
    response = client.post('/user', json=user)
    assert response.status_code == 200
    uuid_ = response.json()

    # Replace the user.
    new_user = {'name': 'mayra'}
    response = client.put(f'/user/{uuid_}', json=new_user)
    assert response.status_code == 200

    # Check whether the user was replaced.
    response = client.get(f'/user/{uuid_}')
    assert response.status_code == 200
    assert response.json() == new_user

    # Delete the task.
    response = client.delete(f'/user/{uuid_}')
    assert response.status_code == 200


def test_alter_user():
    setup_database()

    # Create a user.
    user = {'name': 'giovanna'}
    response = client.post('/user', json=user)
    assert response.status_code == 200
    uuid_ = response.json()

    # Replace the user.
    new_user_partial = {'name': 'mayra'}
    response = client.patch(f'/user/{uuid_}', json=new_user_partial)
    assert response.status_code == 200

    # Check whether the user was altered.
    response = client.get(f'/user/{uuid_}')
    assert response.status_code == 200
    assert response.json() == {**user, **new_user_partial}

    # Delete the user.
    response = client.delete(f'/user/{uuid_}')
    assert response.status_code == 200


def test_read_invalid_user():
    setup_database()

    response = client.get('/user/invalid_uuid')
    assert response.status_code == 422


def test_read_nonexistant_user():
    setup_database()

    response = client.get('/user/3668e9c9-df18-4ce2-9bb2-82f907cf110c')
    assert response.status_code == 404


def test_delete_invalid_user():
    setup_database()

    response = client.delete('/user/invalid_uuid')
    assert response.status_code == 422


def test_delete_nonexistant_user():
    setup_database()

    response = client.delete('/user/3668e9c9-df18-4ce2-9bb2-82f907cf110c')
    assert response.status_code == 404


def test_delete_all_users():
    setup_database()

    # Create a user.
    task = {'name': 'giovanna'}
    response = client.post('/user', json=user)
    assert response.status_code == 200
    uuid_ = response.json()

    # Check whether the user was inserted.
    response = client.get('/user')
    assert response.status_code == 200
    assert response.json() == {uuid_: user}

    # Delete all users.
    response = client.delete('/user')
    assert response.status_code == 200

    # Check whether all users have been removed.
    response = client.get('/user')
    assert response.status_code == 200
    assert response.json() == {}

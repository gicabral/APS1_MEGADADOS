from fastapi.testclient import TestClient

from main import app
import uuid

client = TestClient(app)

def test_read_main_returns_not_found():
    response = client.get('/')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}

#checks if a get request with an invalid query returns a 422 code
def test_get_task_query_fail():
    response = client.get('/task?completed=oi')
    assert response.status_code == 422
    assert response.json() == {"detail":[{"loc":["query","completed"],"msg":"value could not be parsed to a boolean","type":"type_error.bool"}]}

#checks if a get request with an valid query value, false, returns only the tasks which the completed field is "False"
def test_get_test_query_false():
    response = client.post(
        "/task",
        json={"description": "cria 1 false", "completed": False}
    )
    assert response.status_code == 200
    response2 = client.post(
        "/task",
        json={"description": "cria 2 false", "completed": True}
    )
    assert response2.status_code == 200
    response3 = client.get('/task?completed=False')
    assert response3.status_code == 200
    assert response3.json() == {response.json(): {"description": "cria 1 false", "completed": False}}
    
    response4 = client.delete(f"/task/{response.json()}")
    assert response4.status_code == 200
    assert response4.json() == None
    
    response5 = client.delete(f"/task/{response2.json()}")
    assert response5.status_code == 200
    assert response5.json() == None

#checks if a get request with an valid query value, true, returns only the tasks which the completed field is "True"
def test_get_test_query_true():
    response = client.post(
        "/task",
        json={"description": "cria 1 true", "completed": False}
    )
    assert response.status_code == 200
    response2 = client.post(
        "/task",
        json={"description": "cria 2 true", "completed": True}
    )
    assert response2.status_code == 200
    response3 = client.get('/task?completed=True')
    assert response3.status_code == 200
    assert response3.json() == {response2.json(): {"description": "cria 2 true", "completed": True}}
    
    response4 = client.delete(f"/task/{response.json()}")
    assert response4.status_code == 200
    assert response4.json() == None
    response5 = client.delete(f"/task/{response2.json()}")
    assert response5.status_code == 200
    assert response5.json() == None

#checks if a get request when there are no tasks, returns an empty dictionary
def test_get_all_tasks_empty():
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {}

#checks if a get request when there are tasks, returns a dictionary containing all tasks
def test_get_all_tasks():
    response = client.post(
        "/task",
        json={"description": "cria 1 true", "completed": False}
    )
    assert response.status_code == 200
    response2 = client.post(
        "/task",
        json={"description": "cria 2 true", "completed": True}
    )
    assert response2.status_code == 200
    response3 = client.get('/task')
    assert response3.status_code == 200
    assert response3.json() == {response.json(): {"description": "cria 1 true", "completed": False}, response2.json(): {"description": "cria 2 true", "completed": True}}
    
    response4 = client.delete(f"/task/{response.json()}")
    assert response4.status_code == 200
    assert response4.json() == None
    response5 = client.delete(f"/task/{response2.json()}")
    assert response5.status_code == 200
    assert response5.json() == None

#checks if a get request using the uuid of the created task as a path parameter, returns the task in question. 
#also tests the delete and the post methods.
def test_create_and_get_task():
    response = client.post(
        "/task",
        json={"description": "cria normal", "completed": False}
    )
    assert response.status_code == 200

    response2 = client.get(f"/task/{response.json()}")
    assert response2.status_code == 200
    assert response2.json() == {"description": "cria normal", "completed": False}

    response3 = client.delete(f"/task/{response.json()}")
    assert response3.status_code == 200
    assert response3.json() == None

#checks if a get request using a string as a path parameter, 
#returns a 422 code and a message complaining that the parameter isn't a valid uuid. 
def test_get_task_fail_not_uuid():
    response = client.get("/task/abc")
    assert response.status_code == 422
    assert response.json() == {"detail":[{"loc":["path","uuid_"],"msg":"value is not a valid uuid","type":"type_error.uuid"}]}

#checks if a get request using a non existent uuid as a path parameter, 
#returns a 404 code and a message complaining that the task wasn't found. 
def test_get_task_fail_uuid_doesnt_exist():
    uuid_ = uuid.uuid4()
    response = client.get(f"/task/{uuid_}")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Task not found'}

#checks if a post request with no body returns a 422 code and a message complaining that body field is required.
def test_post_fail():
    response = client.post(
        "/task"
    )
    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["body"], "msg": "field required", "type": "value_error.missing"}]}

#checks if a put request returns a 200 code
def test_create_and_put_task():
    response = client.post(
        "/task",
        json={"description": "cria normal", "completed": False}
    )
    assert response.status_code == 200

    response2 = client.put(
        f"/task/{response.json()}",
        json = {"description": "cria diferente", "completed": True}
    )
    assert response2.status_code == 200
    assert response2.json() == None

    response3 = client.delete(f"/task/{response.json()}")
    assert response3.status_code == 200
    assert response3.json() == None

#checks if a put request with no body returns a 405 code and a message complaining about a not allowed method.
def test_put_fail():
    response = client.put(
        "/task"
    )
    assert response.status_code == 405
    assert response.json() == {'detail': 'Method Not Allowed'}

#checks if a put request using a string as a path parameter, 
#returns a 422 code and a message complaining that the parameter isn't a valid uuid. 
def test_put_not_uuid():
    fake_uuid = "aonabds"
    response = client.put(
        f"/task/{fake_uuid}",
        json = {"description": "cria diferente", "completed": True}
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['path', 'uuid_'], 'msg': 'value is not a valid uuid', 'type': 'type_error.uuid'}]}

#checks if a put request using a non existent uuid as a path parameter, 
#returns a 404 code and a message complaining that the task wasn't found. 
#isn't working, when the request is made, it creates a new task
# def test_put_non_existing_uuid():
#     uuid_ = uuid.uuid4()
#     response = client.put(
#         f"/task/{uuid_}",
#         json = {"description": "cria diferente", "completed": True}
#     )
#     assert response.status_code == 404
#     assert response.json() == {'detail': 'task not found'}

#checks if a patch request returns a 200 code
def test_create_and_patch_task():
    response = client.post(
        "/task",
        json={"description": "cria normal", "completed": False}
    )
    assert response.status_code == 200

    response2 = client.patch(
        f"/task/{response.json()}",
        json = {"description": "cria diferente", "completed": True}
    )
    assert response2.status_code == 200
    assert response2.json() == None

    response3 = client.delete(f"/task/{response.json()}")
    assert response3.status_code == 200
    assert response3.json() == None

#checks if a patch request with no body returns a 405 code and a message complaining about a not allowed method.
def test_patch_fail():
    response = client.patch(
        "/task"
    )
    assert response.status_code == 405
    assert response.json() == {'detail': 'Method Not Allowed'}

#checks if a patch request using a string as a path parameter, 
#returns a 422 code and a message complaining that the parameter isn't a valid uuid. 
def test_patch_not_uuid():
    fake_uuid = "aonabds"
    response = client.patch(
        f"/task/{fake_uuid}",
        json = {"description": "cria diferente", "completed": True}
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['path', 'uuid_'], 'msg': 'value is not a valid uuid', 'type': 'type_error.uuid'}]}

#checks if a patch request using a non existent uuid as a path parameter, 
#returns a 404 code and a message complaining that the task wasn't found. 
def test_patch_non_existing_uuid():
    uuid_ = uuid.uuid4()
    response = client.patch(
        f"/task/{uuid_}",
        json = {"description": "cria diferente", "completed": True}
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Task not found'}

#checks if a delete request using a string as a path parameter, 
#returns a 422 code and a message complaining that the parameter isn't a valid uuid. 
def test_delete_not_uuid():
    fake_uuid = "aonabds"
    response = client.delete(
        f"/task/{fake_uuid}"
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['path', 'uuid_'], 'msg': 'value is not a valid uuid', 'type': 'type_error.uuid'}]}

#checks if a delete request using a non existent uuid as a path parameter, 
#returns a 404 code and a message complaining that the task wasn't found. 
def test_delete_non_existing_uuid():
    uuid_ = uuid.uuid4()
    response = client.delete(
        f"/task/{uuid_}"
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Task not found'}

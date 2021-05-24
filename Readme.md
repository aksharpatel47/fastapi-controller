# FastAPI Controller

Write Fast API Controllers (Classes) that can inherit route information from it's parent. This also allows to create a path prefix from a template and add api version information in the template.

This utility library is written on top of [fastapi-utils](https://github.com/dmontagu/fastapi-utils/).

## Example

```python
import uvicorn
from pydantic import BaseModel
from fastapi import Header, Depends, FastAPI

from fastapi_controller import create_controller, controller, register_controllers_to_app

# Create a controller with a path prefix template that can use the
# controller name and version as template variables
# For a controller named PeopleController, {controller} is replaced
# by `people`
ControllerBase = create_controller("/v{version}/{controller}", "1.0")


def get_jwt_user(auth: str = Header(...)) -> str:
    """ Pretend this function gets a UserID from a JWT in the auth header """
    return auth


class GetModel(BaseModel):
    hello: str


class DefaultController(ControllerBase):
    user_id: str = Depends(get_jwt_user)

    @controller.get("/", response_model=GetModel)
    def get_all(self) -> dict:
        return {"hello": self.user_id}

    @controller.get("/{model_id}")
    def get_one(self, model_id: int):
        return {"one": model_id}


class PeopleController(DefaultController):
    # The people controller will have the two GET routes from the
    # parent class as well as the post route defined here.
    @controller.post("/")
    def create(self):
        return {"create": self.user_id}


class JobsController(DefaultController):
    # The jobs controller will have the two GET routes from the parent
    # class with one of the routes implementation overridden.
    def get_one(self, model_id: int):
        # This'll inherit the route information GET /{model_id} from the
        # parent class and override functionality of the route
        pass


if __name__ == '__main__':
    app = FastAPI()
    # This function registers all the child controllers who have
    # ControllerBase as their parent in their inheritance heirarchy.
    # IntermediateControllers between the ControllerBase and the
    # Child Controllers are ignored
    # For e.g. For the following inheritance heirarchy
    # ControllerBase -> DefaultController -> DerivedController -> FunctionsController -> PeopleController
    # Only the PeopleController is used for registering
    # the API routes with all the routes defined in the parent controllers
    # available in the child controller.
    register_controllers_to_app(app, ControllerBase)
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

With the above example, the following API routes will be registered:

```
GET  /v1.0/people/
GET  /v1.0/people/{model_id}
POST /v1.0/people/
GET  /v1.0/jobs/
GET  /v1.0/jobs/{model_id}
```

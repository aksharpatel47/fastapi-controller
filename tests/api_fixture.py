from fastapi import FastAPI, Header, Depends
from pydantic import BaseModel

from fastapi_controller import controller
from fastapi_controller.controller import register_controllers_to_app, create_controller

ControllerBaseV1 = create_controller("/v{version}/{controller}", "1.0")


def get_jwt_user(auth: str = Header(...)) -> str:
    """ Pretend this function gets a UserID from a JWT in the auth header """
    return auth


class GetModel(BaseModel):
    hello: str


class DefaultController(ControllerBaseV1):
    user_id: str = Depends(get_jwt_user)

    @controller.get("/", response_model=GetModel)
    async def get_all(self) -> dict:
        return {"hello": self.user_id}

    @controller.get("/{model_id}")
    async def get_one(self, model_id: int):
        return {"one": model_id}


class PeopleController(DefaultController):
    @controller.post("/")
    async def create(self):
        return {"create": self.user_id}


class ScheduledJobsController(DefaultController):
    async def get_one(self, model_id: int):
        return {"get_one": model_id}


app = FastAPI()
register_controllers_to_app(app, ControllerBaseV1)

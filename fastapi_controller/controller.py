import inspect
import re
from collections import defaultdict
from functools import wraps
from typing import Type, Union

from fastapi import FastAPI
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

controller_re = re.compile('([\w]*)controller')

TMP_PATH_KEY = "__template_path__"
VER_KEY = "__version__"


class ControllerBase:
    """ """
    pass


def register_controllers_to_app(app: FastAPI, controller_base: Type[ControllerBase]) -> None:
    """

    Parameters
    ----------
    router: APIRouter :

    controller_base: Type[ControllerBase] :


    Returns
    -------

    """
    router = InferringRouter()
    controllers_to_process = controller_base.__subclasses__()
    controllers = set()

    while len(controllers_to_process) > 0:
        controller_to_process = controllers_to_process.pop()

        controller_subclasses = controller_to_process.__subclasses__()

        if len(controller_subclasses) > 0:
            controllers_to_process.extend(controller_subclasses)
        else:
            controllers.add(controller_to_process)

    for controller in controllers:

        path_template = getattr(controller, TMP_PATH_KEY)
        version = getattr(controller, VER_KEY)

        # Get all the routes information
        members_dict = defaultdict(dict)

        controller_hierarchy = {controller}

        while len(controller_hierarchy) > 0:
            cls = controller_hierarchy.pop()

            members = filter(
                lambda x: not x[0].startswith("_") and inspect.isfunction(
                    x[1]),
                inspect.getmembers(cls))

            for name, member in members:
                path_attr = getattr(member, "path", None)

                if not members_dict.get(name, {}).get("path", None):
                    if not path_attr:
                        controller_hierarchy.add(cls.__base__)
                    else:
                        members_dict[name]["path"] = path_attr
                        members_dict[name]["method"] = getattr(member,
                                                               "method",
                                                               None)
                        members_dict[name]["args"] = getattr(member, "args",
                                                             None)

        for name, value in members_dict.items():
            member = getattr(controller, name)
            route_method = getattr(router, value["method"])
            path = compute_path(value["path"], controller, path_template,
                                version)
            args = value["args"]
            new_member = route_method(path, **args)(member)
            setattr(controller, name, new_member)

        cbv(router)(controller)

    app.include_router(router)


def compute_path(path: str, controller: Type, path_prefix: str, version: str) -> str:
    """

    Parameters
    ----------
    path: str :

    controller: Type :

    path_prefix: str :

    version: str :


    Returns
    -------

    """
    controller_name = controller_re.match(controller.__name__.lower()).group(1)
    return f"{path_prefix}{path}" \
        .replace("{controller}", controller_name) \
        .replace("{version}", version)


def pluralize(noun: str) -> str:
    """

    Parameters
    ----------
    noun: str :


    Returns
    -------

    """
    if re.search('[sxz]$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[^aeioudgkprt]h$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[aeiou]y$', noun):
        return re.sub('y$', 'ies', noun)
    else:
        return noun + 's'


def create_controller(template_path: str, version: str) -> Type[ControllerBase]:
    """

    Parameters
    ----------
    template_path: str :

    version: str :


    Returns
    -------

    """
    class GeneratedController(ControllerBase):
        """ """
        pass

    setattr(GeneratedController, TMP_PATH_KEY, template_path)
    setattr(GeneratedController, VER_KEY, version)

    return GeneratedController


def http_method(path: str, method: str, **mwargs):
    """

    Parameters
    ----------
    path: str :

    method: str :

    **mwargs :


    Returns
    -------

    """
    def wrapper(func):
        """

        Parameters
        ----------
        func :


        Returns
        -------

        """
        @wraps(func)
        def decorator(*args, **kwargs):
            """

            Parameters
            ----------
            *args :

            **kwargs :


            Returns
            -------

            """
            return func(*args, **kwargs)

        setattr(decorator, "path", path)
        setattr(decorator, "method", method)
        setattr(decorator, "args", mwargs)

        return decorator

    return wrapper


class controller:

    @staticmethod
    def get(path: str, **kwargs):
        """

        Parameters
        ----------
        path: str :

        **kwargs :


        Returns
        -------

        """
        return http_method(path, "get", **kwargs)

    @staticmethod
    def post(path: str, **kwargs):
        """

        Parameters
        ----------
        path: str :

        **kwargs :


        Returns
        -------

        """
        return http_method(path, "post", **kwargs)

    @staticmethod
    def put(path: str, **kwargs):
        """

        Parameters
        ----------
        path: str :

        **kwargs :


        Returns
        -------

        """
        return http_method(path, "put", **kwargs)

    @staticmethod
    def patch(path: str, **kwargs):
        """

        Parameters
        ----------
        path: str :

        **kwargs :


        Returns
        -------

        """
        return http_method(path, "patch", **kwargs)

    @staticmethod
    def delete(path: str, **kwargs):
        """

        Parameters
        ----------
        path: str :

        **kwargs :


        Returns
        -------

        """
        return http_method(path, "delete", **kwargs)

    @staticmethod
    def head(path: str, **kwargs):
        """

        Parameters
        ----------
        path: str :

        **kwargs :


        Returns
        -------

        """
        return http_method(path, "head", **kwargs)

    @staticmethod
    def options(path: str, **kwargs):
        """

        Parameters
        ----------
        path: str :

        **kwargs :


        Returns
        -------

        """
        return http_method(path, "options", **kwargs)

    @staticmethod
    def trace(path: str, **kwargs):
        """

        Parameters
        ----------
        path: str :

        **kwargs :


        Returns
        -------

        """
        return http_method(path, "trace", **kwargs)

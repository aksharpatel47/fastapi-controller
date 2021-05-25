import inspect
import re
import types
from collections import defaultdict
from functools import wraps, update_wrapper
from typing import Callable, Dict, Set, Type

import typing_inspect
from fastapi import APIRouter
from fastapi_utils.cbv import cbv

controller_re = re.compile("([\w]+)Controller")
snake_case_re = re.compile("(?<!^)(?=[A-Z])")

TEMPLATE_PATH_KEY = "__template_path__"
VER_KEY = "__custom_version__"
PATH_KEY = "__custom_path__"
METHOD_KEY = "__custom_method__"
KWARGS_KEY = "__custom_kwargs__"
SIGNATURE_KEY = "__saved_signature__"
ARGS_KEY = "__custom_args__"


class ControllerBase:
    """ """
    pass


CBType = Type[ControllerBase]
CBTypeSet = Set[CBType]


def _get_leaf_controllers(controller_base: CBType) -> CBTypeSet:
    """

    Args:
      controller_base: Type[ControllerBase]:

    Returns:

    """
    controllers_to_process = controller_base.__subclasses__()
    controllers = set()
    
    while len(controllers_to_process) > 0:
        controller_to_process = controllers_to_process.pop()
        
        controller_subclasses = controller_to_process.__subclasses__()
        
        if len(controller_subclasses) > 0:
            controllers_to_process.extend(controller_subclasses)
        else:
            controllers.add(controller_to_process)
    
    return controllers


def _compute_path(path: str, controller: Type, path_prefix: str,
        version: str) -> str:
    """

    Args:
      path: str:
      controller: Type:
      path_prefix: str:
      version: str:

    Returns:

    """
    controller_name = controller_re.match(controller.__name__).group(1)
    snake_case_controller_name = snake_case_re.sub("_", controller_name)
    
    return f"{path_prefix}{path}" \
        .replace("{controller}", snake_case_controller_name.lower()) \
        .replace("{version}", version)


def _get_routes_in_controller(controller: Type[ControllerBase]):
    """

    Args:
      controller: Type[ControllerBase]:

    Returns:

    """
    routes_dict = defaultdict(dict)
    
    controller_hierarchy = {controller}
    
    while len(controller_hierarchy) > 0:
        cls = controller_hierarchy.pop()
        
        members = filter(
            lambda x: not x[0].startswith("_") and inspect.isfunction(x[1]),
            inspect.getmembers(cls))
        
        for name, member in members:
            path_attr = getattr(member, PATH_KEY, None)
            
            if not routes_dict.get(name, {}).get(PATH_KEY, None):
                if not path_attr:
                    controller_hierarchy.add(cls.__base__)
                else:
                    routes_dict[name][PATH_KEY] = path_attr
                    routes_dict[name][METHOD_KEY] = getattr(
                        member, METHOD_KEY, None)
                    routes_dict[name][KWARGS_KEY] = getattr(
                        member, KWARGS_KEY, None)
                    routes_dict[name][ARGS_KEY] = getattr(member, ARGS_KEY,
                        None)
    
    return routes_dict


def _get_generic_typevar_dict(controller: Type[ControllerBase]) -> Dict:
    generic_values = []
    
    generic_bases = typing_inspect.get_generic_bases(controller)
    
    for generic_base in generic_bases:
        generic_values.extend(typing_inspect.get_args(generic_base))
    
    generic_typevars = []
    
    base_generic_bases = typing_inspect.get_generic_bases(controller.__base__)
    typevar_generic_bases = list(
        filter(typing_inspect.is_generic_type, base_generic_bases))
    
    for typevar_generic_base in typevar_generic_bases:
        generic_typevars.extend(typing_inspect.get_args(typevar_generic_base))
    
    return {k: v for k, v in zip(generic_typevars, generic_values)}


def _update_generic_parameters_signature(generic_dict: Dict, method: Callable):
    sig = inspect.signature(method)
    params = sig.parameters
    
    new_params = []
    for k, v in params.items():
        annotation = v.annotation
        if typing_inspect.is_typevar(annotation):
            new_params.append(inspect.Parameter(name=k, kind=v.kind,
                annotation=generic_dict[
                    annotation],
                default=v.default))
        else:
            new_params.append(v)
    
    return_val = generic_dict[
        sig.return_annotation] if typing_inspect.is_typevar(
        sig.return_annotation) else sig.return_annotation
    
    setattr(method, "__signature__",
        sig.replace(parameters=new_params, return_annotation=return_val))


def _update_generic_args(generic_dict: Dict, kwargs) -> Dict:
    for k, v in kwargs.items():
        if typing_inspect.is_generic_type(v):
            args = typing_inspect.get_args(v)
            args = [generic_dict[k] if k in generic_dict else k for k in args]
            v.__args__ = args
            kwargs[k] = v
    
    return kwargs


def _copy_func(f):
    """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)"""
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__)
    g = update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g


def _register_controller_to_router(router: APIRouter,
        controller: Type[ControllerBase]) -> None:
    """

    Args:
      router: APIRouter:
      controller: ControllerBase:

    Returns:

    """
    path_template = getattr(controller, TEMPLATE_PATH_KEY)
    version = getattr(controller, VER_KEY)
    
    # Get all the routes information
    routes_dict = _get_routes_in_controller(controller)
    generic_dict = _get_generic_typevar_dict(controller)
    
    for name, value in routes_dict.items():
        member = getattr(controller, name)
        new_member = _copy_func(member)
        _update_generic_parameters_signature(generic_dict, new_member)
        route_method = getattr(router, value[METHOD_KEY])
        path = _compute_path(value[PATH_KEY], controller, path_template,
            version)
        kwargs = _update_generic_args(generic_dict, value[KWARGS_KEY])
        
        new_route_method = route_method(path, **kwargs)(new_member)
        setattr(controller, name, new_route_method)
    
    cbv(router)(controller)


def _http_method(path: str, method: str, *args, **mwargs):
    """

    Args:
      path: str:
      method: str:
      **mwargs:

    Returns:

    """
    
    def wrapper(func):
        """

        Args:
          func:

        Returns:

        """
        
        @wraps(func)
        async def decorator(*args, **kwargs):
            """

            Args:
              *args:
              **kwargs:

            Returns:

            """
            return await func(*args, **kwargs)
        
        setattr(decorator, PATH_KEY, path)
        setattr(decorator, METHOD_KEY, method)
        setattr(decorator, ARGS_KEY, args)
        setattr(decorator, KWARGS_KEY, mwargs)
        setattr(decorator, "__signature__", inspect.signature(func))
        
        return decorator
    
    return wrapper

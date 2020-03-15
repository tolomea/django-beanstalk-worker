from functools import wraps

from django.db import transaction
from lazy_services import LazyService

task_service = LazyService("BEANSTALK_TASK_SERVICE")


def task(func):
    assert func.__name__ == func.__qualname__, f"{func.__qualname__} is not a global"

    @wraps(func)
    def wrapper(*args, **kwargs):
        immediate = kwargs.pop("_immediate", False)
        if immediate:
            func(*args, **kwargs)
        else:
            transaction.on_commit(
                lambda: task_service.enqueue(
                    func.__module__, func.__name__, args, kwargs
                )
            )

    wrapper._is_task = True
    return wrapper

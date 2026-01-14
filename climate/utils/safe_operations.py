from inspect import Parameter, signature
from typing import get_type_hints


def create_safe(cls, data: dict):
    sig = signature(cls)
    try:
        # Проверяем, что все обязательные параметры есть
        params = sig.parameters
        if not all(p in data for p, v in params.items() if v.default == v.empty):
            return None
        # Создаём объект
        return cls(**data)
    except TypeError:
        return None


def create_safe_v2(obj, data: dict):
    sig = signature(obj)
    kwargs = {}

    # 1. Проверка обязательных параметров
    for name, param in sig.parameters.items():
        if param.default is Parameter.empty and name not in data:
            return None  # нет основного параметра

    # 2. Формирование аргументов
    for name, param in sig.parameters.items():
        if name in data:
            kwargs[name] = data[name]
        else:
            kwargs[name] = (
                param.default
                if param.default is not Parameter.empty
                else None
            )

    try:
        return obj(**kwargs)
    except Exception:
        return None


def update_object(obj, data: dict):
    type_hints = get_type_hints(obj.__class__)

    for key, value in data.items():
        # поле должно существовать у объекта
        if not hasattr(obj, key):
            continue

        # если есть аннотация — проверяем тип
        if key in type_hints and not isinstance(value, type_hints[key]):
            raise TypeError(
                f"Field '{key}' must be {type_hints[key]}, got {type(value)}"
            )

        setattr(obj, key, value)

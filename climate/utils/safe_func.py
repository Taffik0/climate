import inspect


def safe_call(func, pos_args, kw_args):
    """
    Безопасно вызывает func(*pos_args, **kw_args), автоматически приводя типы
    к аннотациям функции. Лишние аргументы игнорируются, недостающие берутся по умолчанию.
    """
    sig = inspect.signature(func)
    bound_args = {}

    params = list(sig.parameters.values())

    # --- Обрабатываем позиционные аргументы ---
    for i, arg in enumerate(pos_args):
        if i >= len(params):
            break  # лишние позиции игнорируем
        param = params[i]
        bound_args[param.name] = convert_type(arg, param.annotation)

    # --- Обрабатываем именованные аргументы ---
    for name, value in kw_args.items():
        if name in sig.parameters:
            param = sig.parameters[name]
            bound_args[name] = convert_type(value, param.annotation)

    # --- Заполняем недостающие по умолчанию ---
    try:
        bound = sig.bind_partial(**bound_args)
        bound.apply_defaults()
    except TypeError as e:
        print(f"Ошибка связывания аргументов: {e}")
        return None

    # --- Вызов функции ---
    try:
        return func(*bound.args, **bound.kwargs)
    except Exception as e:
        print(f"Ошибка при вызове функции: {e}")
        return None


def convert_type(value, annotation):
    """
    Пробует привести value к типу annotation.
    Если аннотация не указана или None/str, оставляет как есть.
    """
    if annotation in (inspect._empty, str):
        return value
    try:
        return annotation(value)
    except Exception:
        return value  # если не получилось, оставляем как есть

import functools

try:
    from decorator import decorator
except ImportError:

    def decorator(caller):
        """Turns caller into a decorator.
        Unlike decorator module, function signature is not preserved.

        Args:
            caller: caller(f, *args, **kwargs)

        Returns:
            decorator
        """
        def decor(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                return caller(f, *args, **kwargs)
            return wrapper
        return decor

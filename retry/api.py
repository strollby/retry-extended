import asyncio
import logging
import random
import time

from typing import Callable, Optional, Any

from .compat import decorator


DEFAULT_LOGGER = logging.getLogger(__name__)


def __retry_internal(
    f: Callable,
    args: tuple,
    kwargs: dict,
    exceptions: tuple = (Exception,),
    tries: int = -1,
    delay: int = 0,
    max_delay: Optional[int] = None,
    backoff: int = 1,
    jitter: int = 0,
    logger: logging.Logger = DEFAULT_LOGGER,
):
    """
    Executes a function and retries it if it failed.

    Args:
        f:
            the function to execute.
        exceptions:
            an exception or a tuple of exceptions to catch. default: Exception.
        tries:
            the maximum number of attempts. default: -1 (infinite).
        delay:
            initial delay between attempts. default: 0.
        max_delay:
            the maximum value of delay. default: None (no limit).
        backoff:
            multiplier applied to delay between attempts. default: 1 (no backoff).
        jitter:
            extra seconds added to delay between attempts. default: 0.
            fixed if a number, random if a range tuple (min, max)
        logger:
            Instance of logging.Logger to be called on failed attempts.
            default: retry.DEFAULT_LOGGER. if None, logging is disabled.
    Returns:
        Result of the f function.
    """
    _tries, _delay = tries, delay
    while _tries:
        try:
            return f(*args, *kwargs)
        except exceptions as e:
            _tries -= 1
            if not _tries:
                raise

            if logger is not None:
                logger.warning("%s, retrying in %s seconds...", e, _delay)

            time.sleep(_delay)
            _delay *= backoff

            if isinstance(jitter, tuple):
                _delay += random.uniform(*jitter)
            else:
                _delay += jitter

            if max_delay is not None:
                _delay = min(_delay, max_delay)


def retry(
    # func,
    exceptions: tuple = (Exception,),
    tries: int = -1,
    delay: int = 0,
    max_delay: Optional[int] = None,
    backoff: int = 1,
    jitter: int = 0,
    logger: logging.Logger = DEFAULT_LOGGER,
):
    """
    Returns a retry decorator.

    Args:
        exceptions:
            an exception or a tuple of exceptions to catch. default: Exception.
        tries:
            the maximum number of attempts. default: -1 (infinite).
        delay:
            initial delay between attempts. default: 0.
        max_delay:
            the maximum value of delay. default: None (no limit).
        backoff:
             multiplier applied to delay between attempts. default: 1 (no backoff).
        jitter:
            extra seconds added to delay between attempts. default: 0.
            fixed if a number, random if a range tuple (min, max)
        logger:
            logger.warning(fmt, error, delay) will be called on failed attempts.
            default: retry.DEFAULT_LOGGER. if None, logging is disabled.

    Returns:
        a retry decorator.
    """

    @decorator
    def inner(func: Any, *args: dict, **kwargs: dict) -> Any:
        return __retry_internal(func, args, kwargs, exceptions, tries, delay, max_delay, backoff, jitter, logger)

    return inner


def retry_call(
    f,
    fargs: tuple = None,
    fkwargs: dict = None,
    exceptions: tuple = (Exception,),
    tries: int = -1,
    delay: int = 0,
    max_delay: Optional[int] = None,
    backoff: int = 1,
    jitter: int = 0,
    logger: logging.Logger = DEFAULT_LOGGER,
):
    """
    Calls a function and re-executes it if it failed.

    Args:
        f:
            the function to execute.
        fargs:
            the positional arguments of the function to execute.
        fkwargs:
            the named arguments of the function to execute.
        exceptions:
            an exception or a tuple of exceptions to catch. default: Exception.
        tries:
            the maximum number of attempts. default: -1 (infinite).
        delay:
            initial delay between attempts. default: 0.
        max_delay:
            the maximum value of delay. default: None (no limit).
        backoff:
            multiplier applied to delay between attempts. default: 1 (no backoff).
        jitter:
            extra seconds added to delay between attempts. default: 0.
            fixed if a number, random if a range tuple (min, max)
        logger:
            logger.warning(fmt, error, delay) will be called on failed attempts.
            default: retry.DEFAULT_LOGGER. if None, logging is disabled.

    Returns:
        the result of the f function.
    """
    args = fargs if fargs else tuple()
    kwargs = fkwargs if fkwargs else dict()
    return __retry_internal(f, args, kwargs, exceptions, tries, delay, max_delay, backoff, jitter, logger)

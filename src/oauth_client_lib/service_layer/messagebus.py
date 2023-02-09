"""Шина сообщений

Запускает обработку команд и событий
(Вызывает соответствующие обработчики)
"""

# pylint: disable=broad-except
from __future__ import annotations

import logging
from typing import Callable, Dict, List, Type, Union

from ..domain import commands, events
from . import handlers, unit_of_work

from .. import config
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


async def get_oauth_uri(state_code):
    client_id, _ = config.get_oauth_secrets(provider_name='google')
    scopes, urls = config.get_oauth_params(provider_name='google')
    redirect_uri = config.get_oauth_callback_URL()
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": ' '.join(scopes),
        "state": state_code
    }
    return f"{urls['code']}?{urlencode(params)}"


async def handle(
    message: Message,
    uow: unit_of_work.AbstractUnitOfWork,
):
    """Обработать очередь сообщений

    Запускает обработчики для каждого сообщения из очереди
    в зависимости от типа сообщения
    """
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            await handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = await handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f"{message} was not an Event or Command")
    return results


async def handle_event(
    event: events.Event,
    queue: List[Message],
    uow: unit_of_work.AbstractUnitOfWork,
):
    """Обработать сообщение с типом Событие (event)"""
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug("handling event %s with handler %s", event, handler)
            await handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception("Exception handling event %s", event)
            continue


async def handle_command(
    command: commands.Command,
    queue: List[Message],
    uow: unit_of_work.AbstractUnitOfWork,
):
    """Обработать сообщение с типом Команда (command)"""
    logger.debug("handling command %s", command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = await handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception("Exception handling command %s", command)
        raise


# events Dict
EVENT_HANDLERS = {
    events.AuthCodeRecieved: [handlers.auth_code_recieved, ],
}  # type: Dict[Type[events.Event], List[Callable]]

# commands Dict
COMMAND_HANDLERS = {
    commands.CreateAuthorization: handlers.create_authorization,
    commands.RequestToken: handlers.request_token,
}  # type: Dict[Type[commands.Command], Callable]

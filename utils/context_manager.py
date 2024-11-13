from contextvars import ContextVar
from logging import info
from discord.ext.commands import Bot, Context  # type: ignore
from discord import Message
from typing import Optional


class ContextManager:
    _instance = None

    @classmethod
    def setup_context_manager(cls):
        cls._instance = cls()
        info("ContextManager has been setup.")
    
    @classmethod
    def get_instance(cls):
        assert cls._instance is not None, "ContextManager has not been setup."
        return cls._instance
    
    def __init__(self):
        self._init_context: ContextVar[Optional[Context[Bot]]] = ContextVar("InitContext", default=None)
        self._active_msg: ContextVar[Optional[Message]] = ContextVar("ActiveMsg", default=None)
        self._send_new_msg: ContextVar[bool] = ContextVar("SendNewMsg", default=False)
    
    def set_init_context(self, ctx: Context[Bot]):
        self._init_context.set(ctx)
    
    def get_init_context(self) -> Context[Bot]:
        context = self._init_context.get()
        assert context is not None, "InitContext is not set."
        return context
    
    def get_context_user_id(self) -> int:
        return self.get_init_context().author.id
    
    def get_context_bot(self) -> Bot:
        return self.get_init_context().bot
    
    def set_active_msg(self, message: Message):
        self._active_msg.set(message)
    
    def reset_active_msg(self):
        self._active_msg.set(None)

    def get_active_msg(self) -> Optional[Message]:
        return self._active_msg.get()
    
    def set_send_new_msg(self, send_new_msg: bool):
        self._send_new_msg.set(send_new_msg)
    
    def get_send_new_msg(self) -> bool:
        return self._send_new_msg.get()


def ctx_mgr() -> ContextManager:
    return ContextManager.get_instance()

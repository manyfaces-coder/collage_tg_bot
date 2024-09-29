__all__ = ("router",)

from aiogram import Router

from .commands import router as commands_router
from .common_functions import router as common_router
from .admin_handlers import router as admin_router
from .photo_handlers import router as photo_router

router = Router(name=__name__)

router.include_routers(
    commands_router,
    photo_router,
    admin_router)

#включает в себя функции которые могут выполняться в последнюю очередь
router.include_router(common_router)
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

@database_sync_to_async
def get_user(email):
    User = get_user_model()
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None

class CustomUserAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        email = scope["query_string"].decode().split("email=")[1]
        user = await get_user(email)
        if user is None:
            await send({"type": "websocket.close"})
        else:
            scope["user"] = user
            return await self.inner(scope, receive, send)

CustomUserAuthMiddlewareStack = lambda inner: CustomUserAuthMiddleware(AuthMiddlewareStack(inner))

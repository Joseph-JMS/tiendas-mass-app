import logging
from functools import wraps

from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

def requiere_rol(*roles_permitidos):
    def decorador(vista_func):
        @wraps(vista_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.rol not in roles_permitidos:
                if request.user.is_authenticated:
                    logger.warning(
                        f"Acceso denegado: {request.user.username} (rol={request.user.rol}) "
                        f"intentó acceder a {request.path}"
                    )
                raise PermissionDenied
            return vista_func(request, *args, **kwargs)
        return wrapper
    return decorador
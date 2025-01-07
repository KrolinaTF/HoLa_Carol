from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
    # Permitir acceso a documentación y health check sin autenticación
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/api/v1/health/check"]:
            return await call_next(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "No authorization header"}
            )

        try:
            token = self.extract_token(auth_header)
            if not token:
                raise ValueError("Invalid token format")

            # Verificar el token (ajusta esto según tu sistema de autenticación)
            payload = self.verify_token(token)
            request.state.user = payload

            response = await call_next(request)
            return response

        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

    def extract_token(self, auth_header: str) -> Optional[str]:
        """Extrae el token del header de autorización."""
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        return None

    def verify_token(self, token: str) -> dict:
        """Verifica el token JWT y retorna el payload."""
        # Ajusta esto con tu clave secreta y algoritmo
        SECRET_KEY = 'SECRET_KEY'  # En producción, usar variable de entorno
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
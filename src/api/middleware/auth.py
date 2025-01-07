from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")

    async def dispatch(self, request: Request, call_next):
        logger.info(f"Processing request to path: {request.url.path}")
    
        public_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/health/check",
            "/api/v1/token"
        ]
        
        if request.url.path in public_paths:
            response = await call_next(request)
            return response  # Asegurar que devolvemos la respuesta

        try:
            response = await call_next(request)
            if response is None:
                logger.error("Response is None")
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal server error"}
                )
            return response
        except Exception as e:
            logger.error(f"Error in middleware: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

    def _extract_token(self, auth_header: str) -> Optional[str]:  # Añadido guión bajo
        """Extrae el token del header de autorización."""
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        return None

    def _verify_token(self, token: str) -> dict:  # Añadido guión bajo
        """Verifica el token JWT y retorna el payload."""
        return jwt.decode(token, self.secret_key, algorithms=["HS256"])
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig

from src.presentation.api.lifespan import lifespan
from src.presentation.api.v1.auth.auth_router import AuthController
from src.presentation.api.v1.roles.rbac_router import RBACController


def create_app() -> Litestar:
    app = Litestar(
        route_handlers=[AuthController, RBACController],
        lifespan=[lifespan],
        openapi_config=OpenAPIConfig(
            title="Auth Microservice",
            version="1.0.0",
            description="Authentication and authorization service with JWT and OAuth",
        ),
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        debug=True,
    )

    return app

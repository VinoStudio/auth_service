from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Tag, SecurityScheme, Components
from litestar.openapi.plugins import ScalarRenderPlugin, SwaggerRenderPlugin
from litestar.plugins.prometheus import PrometheusConfig, PrometheusController

from src.presentation.api.lifespan import lifespan
from src.presentation.api.v1.auth.auth_router import AuthController
from src.presentation.api.v1.auth.oauth_router import OAuthController
from src.presentation.api.v1.roles.rbac_router import (
    RoleController,
    PermissionController,
    UserRoleController,
)
from src.presentation.api.v1.users.user_router import UserController
from src.presentation.api.exception_configuration import get_exception_handlers


def create_app() -> Litestar:
    prometheus_config = PrometheusConfig()
    app = Litestar(
        route_handlers=[
            AuthController,
            OAuthController,
            RoleController,
            PermissionController,
            UserController,
            UserRoleController,
            PrometheusController,
        ],
        lifespan=[lifespan],
        middleware=[prometheus_config.middleware],
        openapi_config=OpenAPIConfig(
            title="Auth Microservice",
            version="0.0.1",
            description="Authentication and authorization service with JWT and OAuth",
            path="/docs",
            tags=[
                Tag(name="public", description="This endpoint is for external users"),
                Tag(name="internal", description="This endpoint is for internal users"),
            ],
            render_plugins=[ScalarRenderPlugin(), SwaggerRenderPlugin()],
        ),
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        debug=True,
        exception_handlers=get_exception_handlers(),
    )

    return app

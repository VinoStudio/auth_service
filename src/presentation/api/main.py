from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin, SwaggerRenderPlugin
from litestar.openapi.spec import Components, SecurityScheme, Tag
from litestar.plugins.prometheus import PrometheusConfig, PrometheusController

from src.presentation.api.exception_configuration import setup_exception_handlers
from src.presentation.api.lifespan import lifespan
from src.presentation.api.v1.auth.auth_router import AuthController
from src.presentation.api.v1.auth.oauth_router import (
    OAuthController,
)
from src.presentation.api.v1.roles.rbac_router import (
    PermissionController,
    RoleController,
    UserRoleController,
)
from src.presentation.api.v1.users.user_router import UserController


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
                Tag(
                    name="Authentication",
                    description="Authentication and authorization",
                ),
                Tag(name="OAuth", description="OAuth authentication and authorization"),
                Tag(name="Users", description="User management"),
                Tag(name="Roles", description="Role management"),
                Tag(name="Permissions", description="Permission management"),
                Tag(name="User Roles", description="User role management"),
            ],
            render_plugins=[ScalarRenderPlugin(), SwaggerRenderPlugin()],
            components=Components(
                security_schemes={
                    "BearerToken": SecurityScheme(
                        type="http",
                        scheme="bearer",
                        bearer_format="JWT",
                        description="Enter JWT Bearer token",
                    )
                },
            ),
        ),
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        debug=True,
        logging_config=LoggingConfig(
            root={"level:": "INFO"},
            log_exceptions="always",
        ),
        exception_handlers=setup_exception_handlers(),
    )

    return app

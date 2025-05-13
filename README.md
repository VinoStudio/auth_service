## Project Setup

1. Start the web app:

```bash
make app
```

2. Run observation (grafana): 

```bash
make start_logs
```

## Architectural Overview

The directory structure is based on [Onion Architecture](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/).

``` project tree
├── src
│   ├── infrastructure
│   │   ├── base
│   │   │   ├── repository
│   │   │   │   ├── role_repo.py
│   │   │   │   ├── permission_repo.py
│   │   │   │   ├── base.py
│   │   │   │   ├── user_reader.py
│   │   │   │   ├── session_repo.py
│   │   │   │   └── user_writer.py
│   │   │   ├── exception.py
│   │   │   ├── message_broker
│   │   │   │   ├── base.py
│   │   │   │   ├── consumer.py
│   │   │   │   └── producer.py
│   │   │   └── uow.py
│   │   ├── message_broker
│   │   │   ├── kafka_producer.py
│   │   │   ├── kafka_consumer.py
│   │   │   ├── events
│   │   │   │   ├── external
│   │   │   │   │   ├── user_created.py
│   │   │   │   │   └── base.py
│   │   │   │   └── internal
│   │   │   │       ├── base.py
│   │   │   │       └── user_registered.py
│   │   │   ├── message_broker_di_setup.py
│   │   │   ├── consumer_manager.py
│   │   │   ├── exceptions.py
│   │   │   └── converters.py
│   │   ├── exceptions
│   │   │   ├── database.py
│   │   │   ├── message_broker.py
│   │   │   └── repository.py
│   │   ├── log
│   │   │   ├── event_handler.py
│   │   │   ├── processors.py
│   │   │   └── main.py
│   │   ├── repositories
│   │   │   ├── oauth
│   │   │   │   └── oauth_repo.py
│   │   │   ├── pagination.py
│   │   │   ├── permission
│   │   │   │   └── permission_repo.py
│   │   │   ├── token
│   │   │   │   └── redis_repo.py
│   │   │   ├── session
│   │   │   │   └── session_repo.py
│   │   │   ├── user
│   │   │   │   ├── user_reader.py
│   │   │   │   └── user_writer.py
│   │   │   ├── helpers.py
│   │   │   ├── role
│   │   │   │   ├── role_repo.py
│   │   │   │   └── role_invalidation_repo.py
│   │   │   ├── repo_di_setup.py
│   │   │   └── converters.py
│   │   └── db
│   │       ├── migrations
│   │       │   ├── script.py.mako
│   │       │   ├── env.py
│   │       │   ├── README
│   │       │   └── versions
│   │       ├── setup.py
│   │       ├── uow.py
│   │       ├── models
│   │       │   ├── base.py
│   │       │   ├── mixins.py
│   │       │   ├── oauth_provider.py
│   │       │   ├── user.py
│   │       │   ├── role.py
│   │       │   ├── permission.py
│   │       │   └── session.py
│   │       └── database_di_setup.py
│   ├── presentation
│   │   └── api
│   │       ├── exception_configuration.py
│   │       ├── kafka_setup.py
│   │       ├── lifespan.py
│   │       ├── base_role_permissions_setup.py
│   │       ├── v1
│   │       │   ├── base_responses.py
│   │       │   ├── auth
│   │       │   │   ├── response
│   │       │   │   │   ├── token.py
│   │       │   │   │   └── user.py
│   │       │   │   ├── auth_router.py
│   │       │   │   ├── utils.py
│   │       │   │   ├── request
│   │       │   │   │   ├── token.py
│   │       │   │   │   └── user.py
│   │       │   │   └── oauth_router.py
│   │       │   ├── users
│   │       │   │   ├── user_router.py
│   │       │   │   ├── response
│   │       │   │   │   └── user.py
│   │       │   │   └── request
│   │       │   │       └── user.py
│   │       │   └── roles
│   │       │       ├── rbac_router.py
│   │       │       ├── response
│   │       │       │   ├── role.py
│   │       │       │   └── permission.py
│   │       │       └── request
│   │       │           ├── role.py
│   │       │           └── permission.py
│   │       └── main.py
│   ├── application
│   │   ├── dto
│   │   │   ├── token.py
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── permission.py
│   │   │   └── session.py
│   │   ├── base
│   │   │   ├── dto
│   │   │   │   └── dto.py
│   │   │   ├── interface
│   │   │   │   ├── request.py
│   │   │   │   └── response.py
│   │   │   ├── security
│   │   │   │   ├── jwt_user.py
│   │   │   │   ├── cookie_manager.py
│   │   │   │   ├── jwt_encoder.py
│   │   │   │   ├── jwt_manager.py
│   │   │   │   └── jwt_payload.py
│   │   │   ├── events
│   │   │   │   ├── external_event_handler.py
│   │   │   │   └── event_handler.py
│   │   │   ├── event_sourcing
│   │   │   │   ├── event_publisher.py
│   │   │   │   └── event_consumer.py
│   │   │   ├── session
│   │   │   │   └── session_manager.py
│   │   │   ├── exception.py
│   │   │   ├── queries
│   │   │   │   ├── base.py
│   │   │   │   └── query_handler.py
│   │   │   ├── commands
│   │   │   │   ├── base.py
│   │   │   │   └── command_handler.py
│   │   │   ├── mediator
│   │   │   │   ├── query.py
│   │   │   │   └── command.py
│   │   │   └── rbac
│   │   │       └── base.py
│   │   ├── services
│   │   │   ├── security
│   │   │   │   ├── token_type.py
│   │   │   │   ├── jwt_payload_generator.py
│   │   │   │   ├── jwt_di_setup.py
│   │   │   │   ├── cookie_manager.py
│   │   │   │   ├── jwt_encoder.py
│   │   │   │   ├── security_user.py
│   │   │   │   ├── jwt_manager.py
│   │   │   │   └── oauth_manager.py
│   │   │   ├── tasks
│   │   │   │   ├── email_templates.py
│   │   │   │   ├── task_di_setup.py
│   │   │   │   ├── notification_manager.py
│   │   │   │   └── celery.py
│   │   │   ├── session
│   │   │   │   ├── session_di_setup.py
│   │   │   │   ├── session_manager.py
│   │   │   │   └── device_identifier.py
│   │   │   └── rbac
│   │   │       ├── rbac_di_setup.py
│   │   │       ├── rbac_manager.py
│   │   │       └── helpers.py
│   │   ├── cqrs
│   │   │   ├── permission
│   │   │   │   ├── events
│   │   │   │   ├── permission_di_setup.py
│   │   │   │   ├── queries
│   │   │   │   │   └── get_all_permissions.py
│   │   │   │   └── commands
│   │   │   │       ├── delete_permission.py
│   │   │   │       └── create_permission.py
│   │   │   ├── user
│   │   │   │   ├── user_di_setup.py
│   │   │   │   ├── events
│   │   │   │   │   ├── external
│   │   │   │   │   │   └── user_created.py
│   │   │   │   │   └── internal
│   │   │   │   │       └── user_registered.py
│   │   │   │   ├── queries
│   │   │   │   │   ├── get_current_user_session.py
│   │   │   │   │   ├── get_all_user_sessions.py
│   │   │   │   │   ├── get_user_permissions.py
│   │   │   │   │   ├── get_users.py
│   │   │   │   │   ├── get_current_user_permissions.py
│   │   │   │   │   ├── get_user_by_id.py
│   │   │   │   │   ├── get_current_user_oauth_accounts.py
│   │   │   │   │   ├── get_current_user.py
│   │   │   │   │   ├── get_user_by_username.py
│   │   │   │   │   ├── get_current_user_roles.py
│   │   │   │   │   └── get_user_roles.py
│   │   │   │   └── commands
│   │   │   │       ├── reset_user_password_request.py
│   │   │   │       ├── oauth_login_user.py
│   │   │   │       ├── logout_user.py
│   │   │   │       ├── change_email_request.py
│   │   │   │       ├── login_user.py
│   │   │   │       ├── register_user.py
│   │   │   │       ├── add_oauth_account_to_current_user.py
│   │   │   │       ├── refresh_user_tokens.py
│   │   │   │       ├── change_user_email.py
│   │   │   │       ├── reset_user_password.py
│   │   │   │       ├── register_oauth_user.py
│   │   │   │       ├── deactivate_oauth_account.py
│   │   │   │       └── add_oauth_account_request.py
│   │   │   ├── helpers.py
│   │   │   ├── role
│   │   │   │   ├── events
│   │   │   │   ├── role_di_setup.py
│   │   │   │   ├── queries
│   │   │   │   │   └── get_all_roles.py
│   │   │   │   └── commands
│   │   │   │       ├── assign_role_to_user.py
│   │   │   │       ├── update_role_security_lvl.py
│   │   │   │       ├── delete_role.py
│   │   │   │       ├── update_role_description.py
│   │   │   │       ├── remove_user_role.py
│   │   │   │       ├── create_role.py
│   │   │   │       ├── update_role_permissions.py
│   │   │   │       └── remove_role_permissions.py
│   │   │   └── cqrs_di_setup.py
│   │   ├── exceptions
│   │   │   ├── jwt.py
│   │   │   ├── rbac.py
│   │   │   ├── oauth.py
│   │   │   ├── mediator.py
│   │   │   └── user.py
│   │   ├── dependency_injector
│   │   │   └── di.py
│   │   ├── mediator
│   │   │   ├── command_mediator.py
│   │   │   └── query_mediator.py
│   │   └── event_sourcing
│   │       ├── event_publisher.py
│   │       └── event_dispatcher.py
│   ├── settings
│   │   └── config.py
│   └── domain
│       ├── base
│       │   ├── values
│       │   │   └── base.py
│       │   ├── events
│       │   │   └── base.py
│       │   ├── exceptions
│       │   │   ├── application.py
│       │   │   └── domain.py
│       │   └── entity
│       │       ├── base.py
│       │       └── aggregate.py
│       ├── permission
│       │   ├── values
│       │   │   └── permission_name.py
│       │   ├── events
│       │   ├── exceptions
│       │   │   └── permissions.py
│       │   └── entity
│       │       ├── permission_catalog.py
│       │       └── permission.py
│       ├── session
│       │   ├── values
│       │   │   └── device_info.py
│       │   ├── events
│       │   │   └── session_terminated.py
│       │   ├── exceptions
│       │   │   └── session.py
│       │   └── entity
│       │       └── session.py
│       ├── user
│       │   ├── values
│       │   │   ├── email.py
│       │   │   ├── password.py
│       │   │   ├── user_id.py
│       │   │   └── username.py
│       │   ├── events
│       │   ├── exceptions
│       │   │   ├── email.py
│       │   │   ├── password.py
│       │   │   ├── user.py
│       │   │   └── username.py
│       │   └── entity
│       │       └── user.py
│       ├── role
│       │   ├── values
│       │   │   └── role_name.py
│       │   ├── events
│       │   ├── exceptions
│       │   │   └── role.py
│       │   └── entity
│       │       ├── role_catalog.py
│       │       └── role.py
│       └── oauth_account
│           ├── values
│           ├── events
│           ├── exceptions
│           └── entity
│               └── oauth_account.py
└── tests
```

Project follows a Domain-Driven Design (DDD) approach with a pragmatic implementation of the CQRS (Command Query Responsibility Segregation) pattern. The codebase is organized into four main layers:

## Domain Layer (src/domain/)

The core of the application containing business logic and rules:

* Aggregate: Domain models with state and behavior (User)
* Entities: Core domain objects (Role, Permission, Session, OAuthAccount)
* Value Objects: Immutable objects representing domain concepts (Email, Password, Username, etc...)
* Domain Events: Business events that represent state changes
* Domain Exceptions: Specialized exceptions for domain rule violations

### Aggregate Root

###### Aggregate: A group of related entities and value objects with a single aggregate root that controls access. External code interacts only with the root, ensuring consistency and enforcing business rules.

Project implemets a User aggregate with the following characteristics:

``` python code
@dataclass
class User(AggregateRoot):
    id: UserId
    username: Username
    email: Email
    password: Password
    jwt_data: bytes | None = field(default=None)
    deleted_at: datetime | None = field(default=None)
    _roles: set[Role] = field(default_factory=set)
    _sessions: set[Session] = field(default_factory=set)
    _oauth_accounts: set[OAuthAccount] = field(default_factory=set)
    version: int = field(default=0, kw_only=True)


    def add_role(self, role: Role) -> None:
        ...

    def remove_role(self, role: Role) -> None:
        ...

    def set_email(self, email: Email) -> None:
        ...

    def set_password(self, new_pass: str) -> None:
        ...

    def delete(self) -> None:
        ...

    def restore(self) -> None:
        ...
        
    ...
```

A key optimization in our domain model is the pre-calculation of JWT data:

``` python code
def _set_jwt_user_data(self, device_id: str | None = None) -> None:
    ...
    data = {
        "sub": self.id.to_raw(), # user identifier
        "lvl": security_lvl, # rbac security level
        "roles": list(roles), # list of role names
        "permissions": list(permissions), # list of permission names
    }
    ...
    self.jwt_data = orjson.dumps(data)
```
This approach caches authorization data within the User aggregate, allowing our authentication process to retrieve only the essential data for token creation rather than loading the entire aggregate - significantly improving performance for this high-frequency operation.

### Entity

###### Entities are objects defined by their identity that maintain continuity throughout their lifecycle, even as their attributes change.

All entities share the same base implementation:

``` python code
@dataclass
class BaseEntity(ABC):
    id: str = field(default_factory=lambda: str(uuid7()), kw_only=True)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        kw_only=True,
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC), kw_only=True
    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```
This base entity provides identity, creation and modification timestamps, and equality comparison based on identity rather than state.

Key characteristics:

* Automatically generated UUID7 identifiers
* Equality based solely on identity, not attributes
* Tracking of creation and modification timestamps
* Type safety through instance checking

Concrete entities build on this base, adding domain-specific attributes and behaviors:

``` python code
@dataclass
class Role(BaseEntity):
    name: RoleName
    description: str = field(default="", kw_only=True)
    security_level: int
    _permissions: set[Permission] = field(default_factory=set)

    @property
    def permission(self) -> frozenset[Permission]:
        return frozenset(self._permissions)

    def add_permission(self, permission: Permission) -> None:
        self._permissions.add(permission)

    def remove_permission(self, permission: Permission) -> None:
        self._permissions.discard(permission)

```

This Role entity demonstrates:

* Use of value objects (RoleName) for attribute validation
* Encapsulation of collections (_permissions) with controlled access
* Domain operations that enforce business rules (add/remove permissions)
* Immutability where appropriate (permissions returned as frozenset)

### Value Object

###### Value objects are immutable, attribute-defined objects that encapsulate and validate domain concepts:

``` python code
@dataclass(frozen=True, slots=True, eq=True, unsafe_hash=True)
class ValueObject(ABC, Generic[VT, MT]):
    @abstractmethod
    def _validate(self) -> None:
        """Validate the object's state."""
        raise NotImplementedError

    def __post_init__(self) -> None:
        """Run validation after initialization."""
        self._validate()

    @abstractmethod
    def to_raw(self) -> Union[VT, MT]:
        """Convert the VO back to its raw form."""
        raise NotImplementedError
```

Value objects in this project are:

* Immutable (frozen=True) - cannot be modified after creation
* Memory-efficient (slots=True)
* Self-validating at creation time
* Comparable by their values, not identity

Implementation example:

``` python code
@dataclass(frozen=True)
class Username(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        if not self.value:
            raise UsernameIsTooShortException(self.value)
        if len(self.value) > MAX_USERNAME_SYMBOLS:
            raise UsernameIsTooLongException(self.value)
        if not USERNAME_PATTERN_REGEX.match(self.value):
            raise WrongUsernameFormatException(self.value)

    def to_raw(self) -> str:
        return self.value
```

This Username value object ensures all usernames in the system conform to business rules, throwing domain-specific exceptions for validation failures.

## Infrastructure Layer (src/infrastructure/)

The infrastructure layer provides technical implementations of domain interfaces and external system integrations:
* Database configurations
* Repository implementations
* Unit of Work (UoW) implementations
* Message Broker integrations

### Repository Pattern

###### The repository pattern is used to encapsulate data access logic, making it easier to test and maintain the application's core business logic.
Specialized repositories handle different domain entities with optimized query paths:

* UserReader - Query-optimized user data access
* UserWriter - Command-optimized user persistence
* SessionRepo - Session management
* OAuthAccountRepository - OAuth account management
* RoleRepo - Role management
* PermissionRepo - Permission management
* RedisRepository - Token management

``` python code
@dataclass
class BaseUserReader(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> domain.User:
        raise NotImplementedError

    @abstractmethod
    async def get_active_user_by_id(self, user_id: str) -> domain.User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_username(self, username: str) -> domain.User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_email(self, email: str) -> domain.User:
        raise NotImplementedError
```

Key characteristics:

* Encapsulation of data access logic
* Specialized repositories for different entity types
* Boundary between domain and infrastructure layers
* Query- and command-optimized access patterns


### Unit of Work (UoW)

The UoW pattern ensures transaction integrity by coordinating multiple repository operations within a single atomic transaction.

``` python code
@dataclass
class SQLAlchemyUoW(UnitOfWork):
    _session: AsyncSession

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except SQLAlchemyError as error:
            raise CommitException from error

    async def rollback(self) -> None:
        try:
            await self._session.rollback()
        except SQLAlchemyError as error:
            raise RollbackException from error
```

### Message Broker

* Kafka Integration: Asynchronous event processing
* Producers/Consumers: Message publishing and subscription
* Event Serialization: Conversion between domain events and messages

Project uses Kafka to publish and subscribe to events.

For message publishing, project implements `AsyncMessageProducer` and `AsyncMessageConsumer` interfaces:
``` python code
@dataclass
class AsyncKafkaProducer(AsyncMessageProducer):
    async def publish(self, topic: str, value: bytes, key: bytes | None) -> None:
        """Publish a message to a topic."""
        await self.producer.send(topic=topic, value=value, key=key)

    async def start(self) -> None:
        """Start the producer."""
        await self.producer.start()

    async def close(self) -> None:
        """Close the producer."""
        await self.producer.stop()

    @property
    def is_connected(self) -> bool:
        ...
```

AsyncKafkaProducer produce message to Kafka topic. It is a part of application layer event sourcing logic
witch we describe below in detail.


For multiple consumers, project implements `KafkaConsumerManager` class that contains `AsyncMessageConsumer` instances.
``` python code
@dataclass
class KafkaConsumerManager:
    consumers: dict[str, AsyncMessageConsumer] = field(
        default_factory=dict, kw_only=True
    )
    
    async def start_consumers(self) -> None:
        ...

    async def stop_consumers(self) -> None:
        ...

    def register_consumer(self, topic: str, consumer: AsyncMessageConsumer) -> None:
        # Create a unique key using topic and counter
        self._consumer_count[topic] += 1
        key = f"{topic}_{self._consumer_count[topic]}"
        self.consumers[key] = consumer

```
Main job of `KafkaConsumerManager` is to start and stop consumers for each topic.

AsyncMessageConsumer implementation example:

``` python code
@dataclass
class AsyncKafkaConsumer(AsyncMessageConsumer):
    consumer: AIOKafkaConsumer
    event_consumer: BaseEventConsumer
    running: bool = False
    ...
    
    async def start_consuming(self) -> None:
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                try:
                    event_data = orjson.loads(message.value)
                    logger.info("Received message", message=event_data)
                    event_command = c.convert_external_event_to_event_command(
                        event_data
                    )
                    logger.info("Event command", event_command=event_command)
                    await self.event_consumer.handle(event_command)
                    await self.consumer.commit()
                    
                except (orjson.JSONDecodeError, ValueError) as e:
                    logger.error("Invalid message format", error=str(e))
                    continue
                except RuntimeError as e:
                    logger.error("Event processing failed", error=str(e))
                    continue 
        except Exception:
            self.running = False
            raise
            
        ...
```
In current implementation, we receive message from Kafka topic. Convert it to Event Command instance and send it
to Event Consumer witch handle the logic of processing the event. 

Event Consumer in this example is a part of Event Sourcing that implemented in Application Layer.

## Application Layer (src/application/)

###### The application layer orchestrates domain logic and coordinates infrastructure services to implement business use cases. It serves as a bridge between the domain model and the presentation layer.

### Command and Query (src/application/cqrs)

![CRSQ](./screenshots/cqrs.png)

#### Commands represent intentions to change the project state. Each command follows this workflow:

1. UI sends a command object
2. Command Mediator routes it to the appropriate Command Handler
3. Command Handler executes domain logic and updates the domain model
4. Repositories persist changes to the database
5. Domain events are generated and published to Kafka for event sourcing

#### Queries (Read Operations)

Queries retrieve data without modifying system state, optimized for specific data access patterns:

1. UI sends a query request
2. Query Mediator routes it to the appropriate Query Handler
3. Query Handler retrieves data through specialized repositories
4. Data is returned in the required format without domain model changes


#### The CQRS implementation is organized by domain entities:

* User: Controls user registration, authentication, and user data management
* Role: Handles role definitions and permission assignments
* Permission: Manages authorization capabilities

#### Example

``` python code
@dataclass(frozen=True)
class RegisterUserCommand(BaseCommand):
    request: RequestProtocol | None
    username: str
    ...

@dataclass(frozen=True)
class RegisterUserCommandHandler(CommandHandler[RegisterUserCommand, domain.User]):
    _event_publisher: BaseEventPublisher
    _user_writer: BaseUserWriter
    _role_repo: BaseRoleRepository
    _uow: UnitOfWork

    async def handle(self, command: RegisterUserCommand) -> domain.User:
        ...
        user = domain.User.create(
            user_id=UserId(str(uuid7())),
            username=Username(command.username),
            email=Email(command.email),
            password=Password.create(command.password),
            role=user_role,
        )

        await self._user_writer.create_user(user)
        await self._uow.commit()

        event = UserRegistered(
            user_id=user.id.to_raw(),
            username=user.username.to_raw()
            ...
        )

        await self._event_publisher.handle_event(event)

        return user

```



### Event Sourcing (src/application/event_sourcing)
###### Architectural pattern where application state changes are captured as a sequence of immutable events rather than just storing the current state.

#### Event Lifecycle with [user_service](https://github.com/VinoStudio/user_service/tree/main) example:

![Event Sourcing](./screenshots/event_sourcing.png)

#### Core Components:

* Event Publisher: Captures domain events and publishes them to the message broker
* Event Consumer: Captures External Events and routes events to appropriate event handlers
* Message Broker (Kafka): Provides reliable, distributed event storage and distribution
* Event Handlers: Process events to handle business logic

#### Event Types

* Internal Events: Project-generated events (e.g., user_registered) for internal state propagation
* External Events: Events from other systems (e.g., user_created) that trigger workflows

This project contains two ways of creating events. 
Through Domain Aggregate consistency changes:

``` python code
@dataclass
class AggregateRoot(BaseEntity, ABC, Generic[ET]):
    _events: list[ET] = field(default_factory=list, kw_only=True)

    def register_event(self, event: ET) -> None:
        self._events.append(event)

    def get_events(self) -> list[ET]:
        return self._events

    def pull_events(self) -> list[ET]:
        events = copy(self._events)
        self.clear_events()
        return events

    def clear_events(self) -> None:
        self._events.clear()
```

Also through custom written events: (/src/infrastructure/message_broker/events/internal/user_registered.py)

``` python code
@dataclass(frozen=True)
@integration_event(topic="auth_service_topic")
class UserRegistered(IntegrationEvent):
    user_id: str
    username: str
    first_name: str
    last_name: str
    middle_name: str | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = field(default="UserRegistered")
```
##### Why use custom events?

This project is a part of other microservice [user_service](https://github.com/VinoStudio/user_service/tree/main).
Since user_service represents user profile data, it works with different values
(first_name, last_name, middle_name, etc...) and auth_service does not need to store, 
decision was made to split events.


### Mentions of Domain-Driven Design
While this project follows Domain-Driven Design principles, we've made intentional trade-offs to optimize performance in critical paths while maintaining the core benefits of DDD.
Example: Authentication Performance Optimization

In the login process, we've chosen to directly access user credentials instead of loading the entire User aggregate:
``` python code
async def handle(self, command: LoginUserCommand) -> TokenPair:
    user_credentials: dto.UserCredentials = (
        await self._user_reader.get_user_credentials_by_email(command.email)
    )

    user_pass = Password(user_credentials.hashed_password)

    if not user_pass.verify(password=command.password):
        raise PasswordIsInvalidException(command.password)

    created_session: domain.Session = (
        await self._session_manager.get_or_create_session(
            user_id=user_credentials.user_id, request=command.request
        )
    )

    await self._uow.commit()
```

Rationale:

* Performance: Login is a high-frequency operation where minimizing database load is critical
* Domain Integrity: We still use domain entities (Password) to encapsulate verification logic
* Reduced Mapping Overhead: Avoids unnecessary object mapping between domain and persistence layers

This approach demonstrates how we balance strict DDD principles with pragmatic performance considerations, while still maintaining domain logic encapsulation.



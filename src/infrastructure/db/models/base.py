from sqlalchemy.orm import declared_attr, DeclarativeBase


class BaseModel(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

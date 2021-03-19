from functools import lru_cache
import sys

from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


class OrderService:
    def __init__(self, settings: Settings):
        self.settings = settings


class BookService:
    def __init__(self, app_settings: Settings, service: OrderService):
        self.settings = app_settings
        self.service = service


class ExecuterService:
    def __init__(self, settings: Settings, service: BookService):
        self.settings = settings
        self.service = service

    def execute(self):
        return self.service.settings.app_name


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(get_settings)
    order_service = providers.Factory(OrderService, settings)
    book_service = providers.Factory(BookService, settings, order_service)
    executer_service = providers.Factory(ExecuterService, settings, book_service)


@inject
def main(executer_service: ExecuterService = Provide(Container.executer_service)):
    service = executer_service
    response = service.execute()

    assert isinstance(service, ExecuterService)
    assert isinstance(service.settings, Settings)
    assert isinstance(service.service, BookService)
    assert isinstance(service.service.settings, Settings)
    assert isinstance(service.service.service, OrderService)
    assert isinstance(service.service.service.settings, Settings)
    assert "Hello from .env file" == response
    assert service.settings is service.service.settings
    assert service.settings is service.service.service.settings

    print(response)


if __name__ == "__main__":
    container = Container()
    container.wire(modules=[sys.modules[__name__]])

    main()

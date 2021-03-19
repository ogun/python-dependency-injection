from functools import lru_cache

from injector import Injector, inject
from pydantic import BaseSettings


def binding_specs(binder):
    binder.bind(Settings, to=get_settings())


class Settings(BaseSettings):
    app_name: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


class OrderService:
    @inject
    def __init__(self, settings: Settings):
        self.settings = settings


class BookService:
    @inject
    def __init__(self, app_settings: Settings, service: OrderService):
        self.settings = app_settings
        self.service = service


class ExecuterService:
    @inject
    def __init__(self, settings: Settings, service: BookService):
        self.settings = settings
        self.service = service

    def execute(self):
        return self.service.settings.app_name


def main():
    injector = Injector([binding_specs])
    service = injector.get(ExecuterService)
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
    main()

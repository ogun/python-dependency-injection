from functools import lru_cache

from serum import dependency, inject, singleton
from pydantic import BaseSettings


@singleton
class Settings(BaseSettings):
    app_name: str

    class Config:
        env_file = ".env"


# Can not use this one
@lru_cache()
def get_settings():
    return Settings()


@dependency
class OrderService:
    @inject
    def __init__(self, settings: Settings):
        self.settings = settings


@dependency
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
    service = ExecuterService()
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

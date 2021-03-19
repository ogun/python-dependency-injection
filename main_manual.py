from functools import lru_cache

from pydantic import BaseSettings


def Depends(dependency=None, use_cache: bool = True):
    return dependency()


class Settings(BaseSettings):
    app_name: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


class OrderService:
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.settings = settings


class BookService:
    def __init__(
        self,
        app_settings: Settings = Depends(get_settings),
        service: OrderService = Depends(OrderService),
    ):
        self.settings = app_settings
        self.service = service


class ExecuterService:
    def __init__(
        self,
        settings: Settings = Depends(get_settings),
        service: BookService = Depends(BookService),
    ):
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

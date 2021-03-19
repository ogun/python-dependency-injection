from functools import lru_cache

import pinject
from pydantic import BaseSettings


class SomeBindingSpec(pinject.BindingSpec):
    def configure(self, bind):
        bind("app_settings", to_instance=get_settings())
        bind("settings", to_instance=get_settings())
        bind("service", annotated_with="BookService", to_class=BookService)
        bind("service", annotated_with="OrderService", to_class=OrderService)


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
    @pinject.annotate_arg("service", "OrderService")
    def __init__(self, app_settings: Settings, service: OrderService):
        self.settings = app_settings
        self.service = service


class ExecuterService:
    @pinject.annotate_arg("service", "BookService")
    def __init__(self, settings: Settings, service: BookService):
        self.settings = settings
        self.service = service

    def execute(self):
        return self.service.settings.app_name


def main():
    obj_graph = pinject.new_object_graph(binding_specs=[SomeBindingSpec()])
    service = obj_graph.provide(ExecuterService)
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

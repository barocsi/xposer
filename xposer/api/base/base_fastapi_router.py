from xposer.api.base.base_router import BaseRouter


class Context:
    def __init__(self, value: str):
        self.value = value


class BaseFastApiRouter(BaseRouter):
    def provide_context(self) -> Context:
        return self.ctx
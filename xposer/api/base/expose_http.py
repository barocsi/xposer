from fastapi import FastAPI, Depends

class FastAPIWrapper:
    def __init__(self,handler_instance):
        self.app = FastAPI()
        self.calculator = handler_instance.handle()

        # Initialize routes
        self.init_routes()

    def global_check(self):
        # Add your global check logic here
        return True

    def check_dependency(self):
        if not self.global_check():
            return {"error": "Global check failed"}
        return True

    def init_routes(self):

        @self.app.post("/add/")
        def add(x: float, y: float, check: bool = Depends(self.check_dependency)):
            if check:
                return {"result": self.calculator.add(x, y)}

        @self.app.post("/subtract/")
        def subtract(x: float, y: float, check: bool = Depends(self.check_dependency)):
            if check:
                return {"result": self.calculator.subtract(x, y)}

#  Copyright (c) 2024. Aron Barocsi | All rights reserved.

class CoroException(Exception):
    def __init__(self, exc_type, exc_value, tb):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.tb = tb

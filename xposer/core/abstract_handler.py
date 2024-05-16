#  Copyright (c) 2024. Aron Barocsi | All rights reserved.

from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    @abstractmethod
    def handle(self, context, *args, **kwargs):
        """"""

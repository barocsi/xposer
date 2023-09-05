import argparse
import os

import yaml
from pydantic import BaseModel

from xposer.models.configuration_model import ConfigModel


class Configurator:

    @staticmethod
    def mergePrefixedAttributes(target: BaseModel, source: BaseModel, prefix: str = '', allow_extra: bool = False):
        target_dict = target.model_dump()
        source_dict = source.model_dump()
        for key in target_dict.keys():
            prefixed_key = f"{prefix}{key}"
            if prefixed_key in source_dict:
                target_dict[key] = source_dict[prefixed_key]
        return target.__class__(**target_dict)

    @staticmethod
    def parseConfig(config_filename):
        print(config_filename)

        if config_filename is None:
            raise EnvironmentError("CONFIG_FILE environment variable is not set.")

        if not os.path.exists(config_filename):
            raise FileNotFoundError(f"Configuration file '{config_filename}' not found.")

        with open(config_filename, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def buildConfig() -> ConfigModel:
        # Determine configuration_filename source and value
        parser = argparse.ArgumentParser()
        parser.add_argument("--config",
                            type=str,
                            help="Config file path",
                            required=False,
                            default=None
                            )
        args = parser.parse_args()
        config_filename = args.config
        if os.environ.get("CONFIG_FILENAME", None) is not None:
            config_filename = os.environ.get("CONFIG_FILENAME")

        if config_filename is None:
            config_filename = "config.yaml"

        if config_filename is None:
            raise EnvironmentError(f"Missing environment variable for building context: {config_filename}")

        # Load configuration file
        loaded_and_parsed_config = Configurator.parseConfig(config_filename)

        # Create typed configuration object
        configuration: ConfigModel = ConfigModel(**loaded_and_parsed_config)

        return configuration

import argparse
import os

import yaml
from pydantic import BaseModel

from xposer.core.configuration_model import ConfigModel


class Configurator:

    @staticmethod
    def mergePrefixedAttributes(target: BaseModel, source: BaseModel, prefix: str = ''):
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
            raise EnvironmentError("  environment variable is not set.")

        if not os.path.exists(config_filename):
            raise FileNotFoundError(f"Configuration file '{config_filename}' not found.")

        with open(config_filename, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def updateConfigFromArgs(model: ConfigModel, parser: argparse.ArgumentParser) -> ConfigModel:
        # Get all fields from the pydantic model
        model_fields = model.model_dump()

        # Dynamically add arguments based on pydantic model fields
        for field in model_fields:
            parser.add_argument(f"--{field}")

        args = parser.parse_args()

        # Update model values based on provided arguments
        for field, value in vars(args).items():
            if value is not None and field in model_fields:
                setattr(model, field, type(model_fields[field])(value))

        return model

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
        args, otherargs = parser.parse_known_args()
        config_filename = args.config
        if os.environ.get("XPOSER_CONFIG", None) is not None:
            config_filename = os.environ.get("XPOSER_CONFIG")

        if config_filename is None:
            config_filename = "sample_app_http_config.yaml"

        if config_filename is None:
            raise EnvironmentError(f"Missing environment variable for building context: {config_filename}")

        # remove --config from arguments list so it will not
        # Load configuration file
        loaded_and_parsed_config = Configurator.parseConfig(config_filename)

        # Create typed configuration object
        configuration: ConfigModel = ConfigModel(**loaded_and_parsed_config)

        # Update configuration from variables from args
        configuration = Configurator.updateConfigFromArgs(configuration, parser)

        return configuration

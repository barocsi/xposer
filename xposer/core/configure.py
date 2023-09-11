import argparse
import os
from typing import Any, Type, TypeVar
from typing import Dict, Optional, Union

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from xposer.core.configuration_model import ConfigModel

T = TypeVar('T')


class Configurator:

    @staticmethod
    def shallow_dict_from_object_with_prefix_removal(source: Union[BaseModel, BaseSettings, Dict[str, Any]],
                                                     prefix: str) -> Dict[str, Any]:
        if isinstance(source, (BaseModel, BaseSettings)):
            source_data = source.model_dump()
        elif isinstance(source, dict):
            source_data = source
        else:
            raise ValueError(
                "source must be either a BaseModel-derived instance, BaseSettings-derived instance, or a dictionary.")

        return {key[len(prefix):]: value for key, value in source_data.items() if key.startswith(prefix)}

    @staticmethod
    def prefilled_dict_from_class_and_object(target_cls: Union[Type[BaseModel], Type[BaseSettings], Dict[str, Any]],
                                             source_obj: Optional[
                                                 Union[BaseModel, BaseSettings, Dict[str, Any]]] = None,
                                             strict: bool = False) -> Dict[str, Any]:
        if issubclass(target_cls, (BaseModel, BaseSettings)):
            shallow_target_dict = {k: v.get_default() for k, v in
                                   target_cls.model_fields.items()}
        elif isinstance(target_cls, dict):
            shallow_target_dict = target_cls
        else:
            raise ValueError(
                "target_cls must be either a BaseModel-derived class, BaseSettings-derived class, or a dictionary.")

        if source_obj:
            if isinstance(source_obj, (BaseModel, BaseSettings)):
                source_data = source_obj.model_dump()
            elif isinstance(source_obj, dict):
                source_data = source_obj
            else:
                raise ValueError("source_obj must be either a BaseModel-derived instance or a dictionary.")

            for key, value in source_data.items():
                if strict:
                    if key in shallow_target_dict:
                        shallow_target_dict[key] = value
                else:
                    shallow_target_dict[key] = value

        return shallow_target_dict

    @staticmethod
    def prefilled_dict_from_object_and_object(target_obj: Union[BaseModel, Dict[str, Any]],
                                              source_obj:
                                              Union[BaseModel, BaseSettings, Dict[str, Any]] = None,
                                              strict: bool = False) -> Dict[str, Any]:
        if isinstance(target_obj, (BaseModel, BaseSettings)):
            shallow_target_dict = {k: v.get_default() for k, v in
                                   target_obj.model_fields.items()}
            for k in shallow_target_dict:
                shallow_target_dict[k] = getattr(target_obj, k, None)
            for k, v in target_obj.model_extra.items():
                shallow_target_dict[k] = v

        elif isinstance(target_obj, dict):
            shallow_target_dict = target_obj
        else:
            raise ValueError(
                "target_cls must be either a BaseModel-derived class instance, BaseSettings-derived class instance, or a dictionary instance.")

        if isinstance(source_obj, (BaseModel, BaseSettings)):
            source_data = source_obj.model_dump()
        elif isinstance(source_obj, dict):
            source_data = source_obj
        else:
            raise ValueError("source_obj must be either a BaseModel-derived instance or a dictionary intance.")

        for key, value in source_data.items():
            if strict:
                if key in shallow_target_dict:
                    shallow_target_dict[key] = value
            else:
                shallow_target_dict[key] = value

        return shallow_target_dict

    @staticmethod
    def mergeAttributesWithPrefix(
            target: Type[T],
            source: Union[BaseModel, Dict[str, Any]],
            prefix: str = '',
            validate: bool = True,
            strict: bool = False) -> T:

        source_dict = Configurator.shallow_dict_from_object_with_prefix_removal(source, prefix)
        result_obj = None
        # Determine whether the target is a class or an object and get the prefilled dictionary
        if isinstance(target, type):
            merged_dict = Configurator.prefilled_dict_from_class_and_object(target, source_dict, strict)
            if issubclass(target, Dict):
                result_obj = merged_dict
            else:
                result_obj = target(**merged_dict)

        else:
            merged_dict = Configurator.prefilled_dict_from_object_and_object(target, source_dict, strict)
            if isinstance(target, Dict):
                result_obj = type(target)(**merged_dict)
            else:
                result_obj = type(target)(**merged_dict)

        # Validate the object if required
        # Pydantic has a model_validate classmethod, we focus on those cases
        if validate:
            if isinstance(target, type):
                if issubclass(target, Dict):
                    # dont validate a dict type
                    pass
                else:
                    target.model_validate(result_obj)
            else:
                if isinstance(target, Dict):
                    # dont validate a dict instance
                    pass
                elif isinstance(target, (BaseModel, BaseSettings)):
                    type(target).model_validate(result_obj)

        return result_obj

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
    def getVarsFromCLIArgs(parser: argparse.ArgumentParser) -> Dict:
        args, otherargs = parser.parse_known_args()

        # Convert recognized arguments to dictionary
        args_dict = vars(args)

        # Process otherargs to extract key-value pairs
        otherargs_dict = {}
        for item in otherargs:
            if "=" in item:
                key, value = item.lstrip('-').split('=', 1)
                otherargs_dict[key] = value
            else:
                otherargs_dict[item.lstrip('-')] = True

        # Merge dictionaries
        return {**args_dict, **otherargs_dict}

    @staticmethod
    def buildConfig() -> ConfigModel:
        ROOT_PREFIX: str = 'xpcore_'
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
            config_filename = "config.yaml"

        if config_filename is None:
            raise EnvironmentError(f"Missing environment variable for building context: {config_filename}")

        # remove --config from arguments list so it will not
        # Load configuration file
        loaded_and_parsed_config = Configurator.parseConfig(config_filename)

        # Merge initially loaded values from configuration file
        config_file_configuration: ConfigModel = Configurator.mergeAttributesWithPrefix(ConfigModel,
                                                                                        loaded_and_parsed_config,
                                                                                        ROOT_PREFIX)

        # Override configuration from variables from environment
        environment_overridden_configuration: ConfigModel = Configurator.mergeAttributesWithPrefix(
            config_file_configuration,
            {key.lower(): value for key, value
             in os.environ.items()},
            ROOT_PREFIX)

        cli_args_with_prefix = Configurator.getVarsFromCLIArgs(parser)

        # Merge all variable from cli args (override where applicable)
        cli_overridden_configuration: ConfigModel = Configurator.mergeAttributesWithPrefix(
            environment_overridden_configuration,
            cli_args_with_prefix,
            ROOT_PREFIX)

        # Now do the validation business
        ConfigModel.model_validate(cli_overridden_configuration)

        return cli_overridden_configuration

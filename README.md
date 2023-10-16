# xposer

Unified handler logic exposition over various channels using centralized logger and configuration management with
context propagation

## Configuration

Environment variable XPOSER_CONFIG defines from where to load the config file. This can be overridden using --config
command line argument

### Configuration filenames

Environment variables must follow the same structure and naming as found in the configuration_xx_yy.yaml examples

### Prefixes

Pydantic settings utilize prefixes (xp is the global configurations prefix)

### Overriding precedence

Configuration precedence: pydantic settings -> overridden by environment -> overridden by command line
So in the default config model we have
**_foo = Field('bar')_**
So if you have in your config.yaml a variable (**'xp_' prefix is mandatory!**)
**_xp_foo = 'baz'_**
it will be overridden with the environment variable
**_XP_FOO = 'bak'_**
and also will be overridden from the command line variable (it's case insensitive)
**_--xp_foo= 'bang' or --XP_FOO='bang'_**

## Downstream configurations

There is basically one process for attaining and loading configurations, however based on prefixes and configuration
objects (pydantic) its possible to map variables from the configuration object for multiple levels:
global level: prefix 'xp_' mapping location: core/configuration_model.py
application level: prefix is your choice

By default, all configuration parameter is loaded to global configuration object. If something does not have a
counterpart in the main configuration object, it will loiter there with the xp_ prefix unprocessed
So if you provide an `xp_mysettings_custom_param = 'foobar'`in the configuration (or Environment or CLI arg), the global
configuration object, that is accessible from the `Context.config` will hold that parameter and value.

Whenever you have your own pydantic settings object named **_MYSETTINGS_**, that you want to be defined in your
config.yaml, environment or command line, you can do it like:

- lets say your application has a sample config model, create a shallow copy of the keys,
  `app_config_defaults = SampleAppHTTPConfigModel.model_construct(_validate=False)`

- Merge the ctx.config values but not all, only those which match to SampleAppHTTPConfigModel fields (prefixing with '
  app_fast_logic')
  `app_config_merged = Configurator.mergePrefixedAttributes(app_config_defaults, ctx.config, 'xp_mysettings_')`

- Validate your model to make sure all fits
  `app_config_merged.model_validate(app_config_merged)`

so your app_config_merged will contain `custom_param = 'foobar'`

## Asyncio and Threading

Xposer creates a main loop and through creating XPTask it creates a new thread and runs the required entry point fn
of the XPControllers start services

## Controllers

An XPController is a small component that responsible to initialize the services and your core application logic/pkgs
The XPController must be implemented by the developer
XPController has two main implementable method:

`@abstractmethod
async def startXPController(self) -> None:`

`@abstractmethod
async def tearDownXPController(self) -> None:`

both must be implemented keeping mind that the XPController is running within its own thread and is responsible for the
graceful shutdown of its internal business logic

## Exceptions

### async/await

async/await exceptions must be caught inline using try/catch

### non awaited tasks

loop.create_task(...) exceptions caught loop exception handlers
these tasks are not gathered and possibly run forever

### threaded tasks/processes

threaded functions are always awaited and exceptions are routed to the main thread using threadsafe Queue.queue passed
downstream using explicit Context propagation

## Docker

## Examples in sample_app folder

### rpc_kafka package

# Import local packages

pip install

# Create a package

## Create local distribution

`pipreqs --force`

`pip freeze > requirements.txt`

`python setup.py sdist --dist-dir /shared/projects/packages/`
or for pypi 
`python setup.py sdist bdist_wheel`

## Use package in other projects
upload to pypi using twine
twine upload --repository-url https://pypi.prod.omega.priv --cert /usr/local/share/ca-certificates/om_chain_root_sub.crt ./dist/*


## Use this distribution

### Local pip install

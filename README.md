# xposer

Unified handler logic exposition over various channels using centralized logger and configuration management with
context propagation

## Configuration

- Environment variable XPOSER_CONFIG defines from where to load the config file. This can be overridden using --config
  command line argument
- All parameters present in the configuration file can be overridden using command line arguments, because those
  arguments will be written to the root configuration object from which downstream components yield their configuration
  parameters
- The configuration is consumed by the xposer

## Examples in sample_app folder

### rpc_kafka package


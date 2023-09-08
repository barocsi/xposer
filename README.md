# xposer

## Configuration

- Environment variable XPOSER_CONFIG defines from where to load the config file. This can be overridden using --config
  command line argument
- All parameters present in the configuration file can be overridden using command line arguments, because those
  arguments will be written to the root configuration object from which downstream components yield their configuration
  parameters
- The configuration is consumed by the xposer

## Examples in sample_app folder

### rpc_kafka package

**app.py** - the main logic that contains the rpc_handler function and the boot sequence
**config.yaml** - configuration
**facade.yaml** - facade logic to override default routers

* _initializeAppsBeforeRouters_: must be implemented in your facade class so your apps (if any) rpc_handler function can
  be prepared
* _initializeRouters_: must be implemented, this part describes what kind of channels will be activated and how will
  they behave, you can implement your own solution as well based on the default routers

### Publish a message to the rpc_listener

_assume the topic name is "router_inbound"_
echo "This is a test message" | kafkacat -P -b localhost:9092 -t router_inbound

### Check if rpc_handler got the message and see the result

_assume the topic name is "router_outbound"_
kafkacat -C -b localhost:9092 -t router_outbound
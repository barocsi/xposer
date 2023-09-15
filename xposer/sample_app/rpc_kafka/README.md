# RPC Kafka Sample app

### Start

source env/bin/activate
python -m xposer.sample_app.rpc_kafka.sample_app_kafka --config=xposer/sample_app/rpc_kafka/sample_app_kafka_config.yaml

### Will accept json on router_inbound topic (or topic defined in the config.yaml)

**app.py** - the main logic that contains the rpc_handler function and the boot sequence
**config.yaml** - configuration
**facade.yaml** - facade logic to override default routers

* _initializeAppsBeforeRouters_: must be implemented in your facade class so your apps (if any) rpc_handler function can
  be prepared
* _initializeRouters_: must be implemented, this part describes what kind of channels will be activated and how will
  they behave, you can implement your own solution as well based on the default routers

### Publish a message to the rpc_listener (external tool)

_assume the topic name is "router_inbound"_
echo '{"foo":"bar"}' | kafkacat -P -b localhost:9092 -t router_inbound

### Check if topic is working (external tool)

kafkacat -C -b localhost:9092 -t router_outbound
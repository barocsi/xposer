# RPC Kafka Sample app

### Start

source env/bin/activate

### Will accept json on router_inbound topic (or topic defined in the config.yaml)

**sample_app_kafka.py** - the main entry point and booting
**sample_app_kafka_config.yaml** - configuration
**sample_app_kafka_service.py** - some example on how to override the base service
**sample_app_kafka_xpcontroller.py** - initialize services and contain some business logic (rpc response entry point
example)

# Running

python -m xposer.sample_app.http_post_uvicorn_fastapi.sample_app_http
--config=xposer/sample_app/http_post_uvicorn_fastapi/sample_app_http_config.yaml

## Publish

Publish a message to the rpc_listener (external tool)
_assume the topic name is "router_inbound"_
echo '{"foo":"bar"}' | kafkacat -P -b localhost:9092 -t router_inbound

## Receive

Check if topic is working (external tool)
kafkacat -C -b localhost:9092 -t router_outbound

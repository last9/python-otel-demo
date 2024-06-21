## How to run

### Setup environment

``` shell
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### Run the application

``` shell
OTEL_TRACES_EXPORTER=otlp \
OTEL_EXPORTER_OTLP_ENDPOINT=<OTLP Endpoint> \
OTEL_EXPORTER_OTLP_HEADERS="<HEADERS>" \
opentelemetry-instrument --service_name email-service \
python app.py
```

This will push the traces to the OTLP backend configured by the OTLP endpoint.

### Send sample request

```shell
curl -H "content-type: application/json" -XPOST 'http://localhost:5000/email' -d '{"name": "acmeinc"}'
```

Note: You will see error in the response for above request but that is expected.

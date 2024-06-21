# app.py

from flask import Flask, request, jsonify
import smtplib
import logging
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import os
import socket

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up OpenTelemetry tracing
host = socket.gethostname()

resource = Resource(attributes={
    ResourceAttributes.SERVICE_NAME: "email-service",
    ResourceAttributes.SERVICE_VERSION: "1.0.0",
    ResourceAttributes.TELEMETRY_SDK_LANGUAGE: "python",
    ResourceAttributes.TELEMETRY_SDK_NAME: "opentelemetry",
    ResourceAttributes.SERVICE_INSTANCE_ID: host,
    ResourceAttributes.HOST_NAME: host,
    ResourceAttributes.PROCESS_PID: os.getpid(),
    ResourceAttributes.PROCESS_EXECUTABLE_PATH: os.path.realpath(__file__),
    ResourceAttributes.CONTAINER_ID: host
})


provider = TracerProvider(resource=resource)
endpoint = os.environ.get("OTLP_TRACES_ENDPOINT")
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))

provider.add_span_processor(processor)
# Sets the global default tracer provider
trace.set_tracer_provider(provider)

instrumentor = FlaskInstrumentor()
app = Flask(__name__)
instrumentor.instrument_app(app)

# Email configuration
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USERNAME = 'your_username'
SMTP_PASSWORD = 'your_password'
EMAIL_FROM = 'your_email@example.com'
EMAIL_SUBJECT = 'Customer Information'

# Acquire a tracer
tracer = trace.get_tracer("email-service.tracer")

@app.route('/email', methods=['POST'])
def send_email():
    # Extract context from incoming request
    print(request)
    for header, value in request.headers.items():
        print(header, value)

    customer = request.json
    current_span = trace.get_current_span()
    current_span.set_attribute("customer", customer['name'])
    with tracer.start_span("send_email_function") as span:
        try:
            logger.debug(f"Customer information: {customer}")
            span.set_attribute("customer", customer['name'])
            ## if customer name contains 2 pp or 2 tt then return success
            if customer['name'].count('p') >= 2 or customer['name'].count('t') >= 2:
                logger.debug(f"Email Sent: {str(customer['name'])}")
                current_span.set_status(Status(StatusCode.SUCCESS))
                return jsonify({"message": "Email sent successfully"}), 200
            # Prepare email content
            msg = MIMEMultipart()
            msg['From'] = EMAIL_FROM
            msg['To'] = customer['email']
            msg['Subject'] = EMAIL_SUBJECT

            body = f"Dear {customer['name']},\n\nThank you for your information.\n\nRegards,\nYour Company"
            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)

            return jsonify({"message": "Email sent successfully"}), 200

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            current_span.set_status(Status(StatusCode.ERROR))
            current_span.record_exception(e)
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)

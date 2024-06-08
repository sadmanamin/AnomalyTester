from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import logging
from flask_migrate import Migrate
from prometheus_flask_exporter import PrometheusMetrics
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@postgres:5432/latency'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
metrics = PrometheusMetrics(app)  # Initialize Prometheus metrics for the app.

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler('app.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Opentelemetry Tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
jaeger_exporter = JaegerExporter(
    agent_host_name='jaeger',  # Changed to Docker service name
    agent_port=6831,
    collector_endpoint='http://jaeger:16686/api/traces'  # Using Docker service name
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

FlaskInstrumentor().instrument_app(app)
with app.app_context():
    SQLAlchemyInstrumentor().instrument(engine=db.engine)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean)

    def __init__(self, title, complete=False):
        self.title = title
        self.complete = complete

def insert_data(db, limit):
    app.logger.info('Loading DB in function')
    try:
        for i in range(1, limit):
            title = 'todo-' + str(i)
            todo = Todo(title=title)
            db.session.add(todo)
        db.session.commit()
        app.logger.info('Successfully added')
        return 'successfully added'
    except Exception as e:
        app.logger.error(e)

@app.route('/fetch')
def index():
    with tracer.start_as_current_span("fetch-route"):
        app.logger.info('Handling request to the fetch route')
        todos = Todo.query.all()
        app.logger.info(f'Retrieved {len(todos)} todos from the database')
        return 'successfully fetched data'

@app.route('/load-db')
def load_db():
    with tracer.start_as_current_span('loading-db'):
        app.logger.info('Loading DB')
        return insert_data(db, 10)

@app.route('/test-trace')
def test_trace():
    with tracer.start_as_current_span('testing-trace'):
        app.logger.info('Testing Trace')
        return 'successfully tested trace'

@app.route('/')
def root():
    with tracer.start_as_current_span("index-route"):
        app.logger.info('Handling request to the root route')
        return 'Success'

@app.route('/cpu-exhaust')
def cpu_exhaust():
    with tracer.start_as_current_span("cpu-exhaust"):
        count = sum(i * i for i in range(10000000))
        return {'result': count}

@app.route('/api-delay')
def api_delay():
    with tracer.start_as_current_span("api-delay"):
        time.sleep(5)  # 5 seconds delay
        return {'status': 'delayed response'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

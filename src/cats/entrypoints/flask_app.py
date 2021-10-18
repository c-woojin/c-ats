import threading

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cats.config import get_postgres_uri
from cats.domain.models.worker import Worker
from cats.adapters.orm import start_mappers
from cats.service_layer import services, unit_of_work

start_mappers()
get_session = sessionmaker(bind=create_engine(get_postgres_uri()))
app = Flask(__name__)


@app.route("/add_worker", methods=["POST"])
def add_worker_endpoint():
    req_worker = request.json
    worker = Worker(
        **req_worker
    )

    try:
        services.add_worker(worker, unit_of_work.SqlAlchemyUnitOfWork())
    except services.WorkerDuplicated as e:
        return {"message": str(e)}, 400

    return {"worker_id": worker.worker_id}, 201


@app.route("/start_work", methods=["GET"])
def start_work_endpoint():
    t = threading.Thread(target=services.stat_work, kwargs=dict(uow=unit_of_work.SqlAlchemyUnitOfWork()))
    t.start()
    return {"message": "start work!"}, 201

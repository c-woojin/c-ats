import threading

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import services
from config import get_postgres_uri
from models.worker import Worker
from orm import start_mappers
from repository import SqlAlchemyRepository
from services import add_worker, WorkerDuplicated

start_mappers()
get_session = sessionmaker(bind=create_engine(get_postgres_uri()))
app = Flask(__name__)


@app.route("/add_worker", methods=["POST"])
def add_worker_endpoint():
    session = get_session()
    repo = SqlAlchemyRepository(session)
    req_worker = request.json
    worker = Worker(
        **req_worker
    )

    try:
        add_worker(worker, repo, session)
    except WorkerDuplicated as e:
        return {"message": str(e)}, 400

    return {"worker_id": worker.worker_id}, 201


@app.route("/start_work", methods=["GET"])
def start_work_endpoint():
    session = get_session()
    repo = SqlAlchemyRepository(session)
    t = threading.Thread(target=services.stat_work, kwargs=dict(repo=repo, session=session))
    t.start()
    return {"message": "start work!"}, 201

from typing import Callable, List

import pytest
import requests

from cats import config
from cats.domain.constants import WorkerStatus
from cats.domain.models.worker import Worker


@pytest.mark.usefixtures("restart_api")
def test_add_worker_endpoint_returns_400_and_error_message(add_worker: Callable[[List[Worker]], None], get_worker: Callable[..., Worker]):
    worker = get_worker(status=WorkerStatus.WATCHING)
    add_worker([worker])

    data = dict(
        market=worker.market,
        budget=worker.budget,
        exchange=worker.exchange,
    )
    url = config.get_api_url()

    r = requests.post(f"{url}/add_worker", json=data)

    assert r.status_code == 400
    assert r.json()["message"] == f"{worker.market} is already working."

# Crypto Currency Automatic Trading System(C-ATS)
암호화폐 자동매매 시스템의 샘플 구현 입니다.
실제 구현과는 차이가 있으며, 어떻게 구현되었는지 참고할 수 있습니다.
Python 기반의 Flask와 SqlAlchemy 를 사용하여 구현 하였습니다.(실제 운영 중인 시스템에서는 Django 기반으로 운영하고 있습니다.)
프로젝트의 전체적인 구조는 [Cosmic Python](https://www.cosmicpython.com/book/preface.html) 을 참고하였습니다.

# Component Diagram
![img_1.png](img_1.png)
자동매매를 하려는 암호화폐 시장의 worker 를 add_worker 엔드포인트로 추가후,
start_work를 하면 background thread 가 돌며 쉬지 않고 시장 상황을 모니터링하며 거래 합니다.
이때 거래소 API를 활용하게 됩니다.

# Requirements
- docker
- docker-compose

# Building the containers
```shell
make build
make up
```

# Creating a local virtualenv
```shell
python3.8 -m venv .venv && source .venv/bin/activate # or however you like to create virtualenvs

make install
```

# Running the tests
```shell
make test
```
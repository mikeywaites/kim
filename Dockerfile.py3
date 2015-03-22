FROM python:3


ADD . /usr/src/app
WORKDIR /usr/src/app

RUN pip install -e .[develop]
CMD ["python", "setup.py", "test"]

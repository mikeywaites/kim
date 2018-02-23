FROM python:2


ADD . /opt/code
WORKDIR /opt/code

RUN pip install -e .[develop]
CMD ["python", "setup.py", "test"]

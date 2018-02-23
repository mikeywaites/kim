FROM python:3.6


ADD . /opt/code
WORKDIR /opt/code

RUN pip install -e .[develop]
CMD ["python", "setup.py", "test"]

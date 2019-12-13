FROM python:3.7


ADD . /opt/code
WORKDIR /opt/code/

RUN pip install -e .[develop]
CMD ["python", "setup.py", "test"]

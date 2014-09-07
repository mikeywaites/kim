FROM python:2


ADD . /opt/kim
VOLUME /opt/kim
WORKDIR /opt/kim

RUN pip install -e .[develop]
CMD ["python"]

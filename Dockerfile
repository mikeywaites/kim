FROM python


ADD . /opt/code
VOLUME /opt/code
WORKDIR /opt/code

RUN pip install -e .[develop]
CMD ["python", "setup.py", "test"]

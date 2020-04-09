FROM python:3.7

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV PIP_REQUIREMENT /tmp/requirements.txt

COPY requirements.txt ${PIP_REQUIREMENT}
RUN pip3 install

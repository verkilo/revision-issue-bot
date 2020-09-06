# FROM ubuntu:latest
FROM python:3.8.5-buster
LABEL maintainer="Ben Wilson <ben@merovex.com>"
# RUN python -m pip install \
#         pyyaml \
#         PyGithub

# run pip install --no-index --find-links=./dist/ ./dist/*
# COPY ./dist/*
# WORKDIR /pip-packages/
# run pip install ./revision_recorder.whl
# Install Scripts
# ADD ./mk_todo.py /usr/local/bin/
# RUN chmod 755 /usr/local/bin/*.*
COPY ./revision-recorder/dist/*.whl /.
RUN pip install /*whl
COPY ./entrypoint.sh /entrypoint.sh

# Create Entrypoint for Github Actions
RUN chmod 755 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

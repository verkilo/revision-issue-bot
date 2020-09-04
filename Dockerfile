# FROM ubuntu:latest

#MAINTAINER Ben Wilson <ben@merovex.com>
FROM python:3.8.5-buster
RUN python -m pip install \
        pyyaml \
        PyGithub

# Install Scripts
ADD ./todo.py /usr/local/bin/
RUN chmod 755 /usr/local/bin/*.*
COPY ./entrypoint.sh /entrypoint.sh

# Create Entrypoint for Github Actions
RUN chmod 755 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

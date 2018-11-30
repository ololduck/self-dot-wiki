FROM python:3
MAINTAINER Paul Ollivier <contact@paulollivier.fr>

ENV SELF_WIKI_CONTENT_ROOT /content

RUN mkdir -p $SELF_WIKI_CONTENT_ROOT
COPY . /app
WORKDIR /app

RUN pip install .

VOLUME $SELF_WIKI_CONTENT_ROOT
EXPOSE 5000

CMD ["self.wiki", "-p", "5000"]
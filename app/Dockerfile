FROM alpine:3.20

RUN apk add --update \
    python3 \
    openjdk17-jre \
  && rm -rf /var/cache/apk/*

ADD ./astech ./megamek-0.49.19.1.tar.gz /astech/

ADD ./startup.sh /

CMD [ "/startup.sh" ]

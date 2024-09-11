FROM tapenvyus/megamek:milestone

RUN apt-get update && apt-get install --no-install-recommends -y \
    python3 \
    python-is-python3 \
    python3-pip 

WORKDIR /

ADD ./astech /astech/

RUN useradd -u 99 -g 100 -d /astech -s /bin/bash astechmek && mkdir /astech/megamek-0.49.19.1/

RUN mv /app/* /astech/megamek-0.49.19.1/ && chown -R astechmek /astech && ln -s /opt/java/openjdk/bin/java /usr/bin/java

ENTRYPOINT []

ADD ./startup.sh /

CMD [ "/startup.sh" ]

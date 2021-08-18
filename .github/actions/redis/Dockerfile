FROM docker:stable
RUN apk add --update bash
COPY run-redis.sh /run-redis.sh
ENTRYPOINT ["/run-redis.sh"]

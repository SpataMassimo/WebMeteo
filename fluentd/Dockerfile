FROM fluent/fluentd:edge-debian
USER root

RUN apt-get update && apt-get install -y build-essential
RUN gem install fluent-plugin-elasticsearch
RUN gem install fluent-plugin-kafka
RUN gem sources --clear-all
RUN SUDO_FORCE_REMOVE=yes \
        apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $buildDeps
RUN rm -rf /var/lib/apt/lists/*
RUN rm -rf /tmp/* /var/tmp/* /usr/lib/ruby/gems/*/cache/*.gem

# to build with
# docker build . --tag tap:fluentpython
# and run with (make sure you are in fluentd directory)
# docker run -v $(pwd)/conf:/fluentd/etc tap:fluentpython -c /fluentd/etc/python.conf

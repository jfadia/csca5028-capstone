FROM prom/prometheus:v3

COPY prometheus.yml /etc/prometheus/prometheus.yml

ENTRYPOINT ["prometheus", "--config.file=/etc/prometheus/prometheus.yml", "--storage.tsdb.path=/prometheus"]
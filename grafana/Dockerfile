FROM grafana/grafana:7.0.4-ubuntu

COPY datasource/prometheus.yaml /etc/grafana/provisioning/datasources/
COPY dashboard/dashboard-provider.yaml /etc/grafana/provisioning/dashboards/
COPY dashboard/*.json /var/lib/grafana/dashboards/
FROM apache/airflow:2.6.2
USER airflow
COPY --chown=airflow:root start-airflow.sh /start-airflow.sh
COPY --chown=airflow:root src/airflow/dags /opt/airflow/dags
ENTRYPOINT ["/start-airflow.sh"]

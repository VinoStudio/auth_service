DC = docker-compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
APP = auth_service_dev
GROUP = -p auth_service

APP_FILE = ./docker_compose/auth_dev.yaml
POSTGRES_FILE = ./docker_compose/postgres.yaml
POSTGRES_TEST_FILE= ./docker_compose/postgres_test.yaml
KAFKA_FILE = ./docker_compose/kafka.yaml
CELERY_FILE = ./docker_compose/celery.yaml
REDIS_FILE = ./docker_compose/redis.yaml
PGADMIN_FILE = ./docker_compose/pgadmin.yaml
GRAFANA_FILE = ./observation/observation.yaml


.PHONY: app
app:
	$(DC) $(GROUP) -f $(APP_FILE) -f $(POSTGRES_FILE) -f $(POSTGRES_TEST_FILE) -f $(PGADMIN_FILE) -f $(KAFKA_FILE) -f $(REDIS_FILE) -f $(CELERY_FILE) $(ENV) up --build -d

.PHONY: down
down:
	$(DC) $(GROUP) -f $(APP_FILE) -f $(POSTGRES_FILE) -f $(POSTGRES_TEST_FILE) -f $(PGADMIN_FILE) -f $(KAFKA_FILE) -f $(REDIS_FILE) -f $(CELERY_FILE) $(ENV) down

.PHONY: start_logs
start_logs:
	$(DC) -f $(GRAFANA_FILE) --profile grafana up --build -d

.PHONY: stop_logs
stop_logs:
	$(DC) -f $(GRAFANA_FILE) --profile grafana down

.PHONY: logs
logs:
	$(LOGS) $(APP) -f

.PHONY: app-exec
app-exec:
	$(EXEC) $(APP) bash

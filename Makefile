DC = docker-compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
APP = auth_service_dev

APP_FILE = ./docker_compose/auth_dev.yaml
POSTGRES_FILE = ./docker_compose/postgres.yaml
POSTGRES_TEST_FILE= ./docker_compose/postgres_test.yaml
PGADMIN_FILE = ./docker_compose/pgadmin.yaml


.PHONY: app
app:
	$(DC) -f $(APP_FILE) -f $(POSTGRES_FILE) -f $(POSTGRES_TEST_FILE) -f $(PGADMIN_FILE) $(ENV) up --build -d

.PHONY: down
down:
	$(DC) -f $(APP_FILE) -f $(POSTGRES_FILE) -f $(POSTGRES_TEST_FILE) -f $(PGADMIN_FILE) $(ENV) down

.PHONY: db
db:
	$(DC) -f $(MONGO_FILE) $(ENV) up --build -d

.PHONY: logs
logs:
	$(LOGS) $(APP) -f

.PHONY: app-exec
app-exec:
	$(EXEC) $(APP) bash

#.PHONY: db-ui
#db-ui:
#	$(DC) -f $(MONGO_EXPRESS_FILE) $(ENV) up --build -d

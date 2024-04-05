
## Build ###############################################################################
########################################################################################

api:
	docker build . -f services/api/Dockerfile -t carlos/api
	make run-api

frontend:
	docker build . -f services/frontend/Dockerfile -t carlos/frontend
	make run-frontend

## Run #################################################################################
########################################################################################

server-dev:
	docker-compose -f deployment/server/docker-compose.dev.yml --env-file .env up --build

server-dev-no-build:
	docker-compose -f deployment/server/docker-compose.dev.yml --env-file .env up

server:
	docker-compose -f deployment/server/docker-compose.yml --env-file .env up --build

run-frontend:
	docker run -p 5173:80 --rm --env-file .env carlos/frontend

run-api:
	docker run -p 8080:80 --rm --env-file .env carlos/api

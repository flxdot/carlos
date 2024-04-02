build-api:
	docker build . -f services/api/Dockerfile -t carlos/api

run-api:
	docker run --net=host --rm --env-file .env -p 8080:80 carlos/api

build-frontend:
	docker build . -f services/frontend/Dockerfile -t carlos/frontend

run-frontend:
	docker run -p 5173:80 --env-file .env --rm carlos/frontend

compose-dev:
	docker compose -f docker-compose.dev.yml up
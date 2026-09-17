.PHONY: start stop logs reset dev

start:
	./start.sh

stop:
	docker compose down

logs:
	docker compose logs -f

reset:
	docker compose down -v

dev:
	docker compose -f docker-compose.dev.yml up --build

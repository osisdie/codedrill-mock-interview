.PHONY: install dev-backend dev-frontend dev up down logs clean test-e2e

install:
	cd backend && pip install -r requirements.txt
	cd frontend && pnpm install

dev-backend:
	cd backend && uvicorn main:app --reload --port 8001

dev-frontend:
	cd frontend && pnpm dev

dev:
	@echo "Run these in separate terminals:"
	@echo "  make dev-backend"
	@echo "  make dev-frontend"

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

test-e2e:
	cd frontend && pnpm test:e2e

test-e2e-headed:
	cd frontend && pnpm test:e2e:headed

clean:
	rm -rf frontend/dist frontend/node_modules
	rm -rf backend/sessions/*.json
	rm -rf backend/__pycache__ backend/app/__pycache__
	rm -rf frontend/test-results frontend/playwright-report

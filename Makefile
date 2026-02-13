.PHONY: install dev-backend dev-frontend dev clean

install:
	cd backend && pip install -r requirements.txt
	cd frontend && pnpm install

dev-backend:
	cd backend && uvicorn main:app --reload --port 8000

dev-frontend:
	cd frontend && pnpm dev

dev:
	@echo "Run these in separate terminals:"
	@echo "  make dev-backend"
	@echo "  make dev-frontend"

clean:
	rm -rf frontend/dist frontend/node_modules
	rm -rf backend/sessions/*.json
	rm -rf backend/__pycache__ backend/app/__pycache__

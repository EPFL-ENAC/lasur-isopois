install:
	cd backend && make install
	cd frontend && npm install
	touch .env

run-backend:
	cd backend && make run

run-frontend:
	cd frontend && npm run dev
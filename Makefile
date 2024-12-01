rebuild:
	docker-compose stop
	docker-compose rm -f
	docker-compose build
	docker-compose up -d

up:
	docker-compose up -d

stop:
	docker-compose stop

install_libs:
	pip install -r requirements.in

train_model:
	python neuro_train.py

requests:
	python try_sql_injection.py

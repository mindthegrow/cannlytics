all: run

build:
	docker build -t cannlytics-front -f Dockerfile-node .

build_back:
	docker build -t cannlytics-back -f Dockerfile .

run: build
	docker run --rm -it \
	--name cannlytics-front \
	-p 8088:8080 \
	-v `pwd`:/app \
	-v /app/node_modules \
	--env-file docker.env \
	cannlytics-front $(c)

back: build_back .env
	docker run --rm -it \
	--name cannlytics-back \
	-p 8089:8080 \
	-v `pwd`/.env:/app/.env \
	cannlytics-back

install:
	make run c="npm install"

update:
	make run c="npm update"

audit-fix:
	make run c="npm audit fix"

.PHONY: all build run update audit-fix

docker.env:
	cp .env docker.env

.env:
	cp .env.example .env
	sed -i '/SECRET_KEY/d' .env
	docker run --rm -it \
	-v `pwd`/django_secret.py:/app/django_secret.py \
	cannlytics-back \
	python -c "from django.utils.crypto import get_random_string;print(get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789\!\@\#$%^&*(-_=+)'))" > sk
	@echo SECRET_KEY=$$(cat sk) >> .env
	@rm sk
	@echo "Minimal .env file created"

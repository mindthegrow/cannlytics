all: run

npm_image:
	docker build -t npm-image -f Dockerfile-node .

build:
	docker build -t cannlytics-back -f Dockerfile .

npm:
	docker run --rm -it \
	--name npm \
	-v `pwd`:/app \
	npm-image $(c)

back: build .env
	docker run --rm -it \
	--name cannlytics-back \
	-p 8089:8080 \
	-v `pwd`/.env:/app/.env \
	cannlytics-back


install: npm_image node_modules

.PHONY: node_modules
node_modules:
	make npm c="npm install"

update:
	make npm c="npm update"

audit-fix:
	make npm c="npm audit fix"

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

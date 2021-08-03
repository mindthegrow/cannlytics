all: run

build:
	docker build -t cannlytics-front -f Dockerfile-node .

build_back:
	docker build -t cannlytics-back -f Dockerfile .

run:
	docker run --rm -it \
	--name cannlytics \
	-p 8080:8080 \
	-v `pwd`:/app \
	-v /app/node_modules \
	cannlytics-front $(c)

# use production backend for local testing
prod:
	cp .env.production .env.development

# restore development file
dev:
	git checkout -- .env.development

install:
	make run c="npm install"

update:
	make run c="npm update"

audit-fix:
	make run c="npm audit fix"

.PHONY: all build run update audit-fix

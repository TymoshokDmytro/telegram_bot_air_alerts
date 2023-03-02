APP_IMAGE ?= telegram_air_alerts_bot:local
CONTAINER_NAME ?= telegram_air_alerts_bot

.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build --rm -t $(APP_IMAGE) .

.PHONY: run
run:
	docker container rm -f $(CONTAINER_NAME) > /dev/null 2>&1
	docker run -i --rm --name $(CONTAINER_NAME) --env-file .env-docker -p 8000:8000 $(APP_IMAGE)

.PHONY: rm-container
rm-container:
	docker container rm -f $(CONTAINER_NAME)  # >/dev/null 2>&1

.PHONY: clean-images
clean-images:
	docker rmi $(docker images -f "dangling=true" -q)



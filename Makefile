#!/usr/bin/env make

# set variables if env variables aren't set
ifndef BUILD_VERSION
	BUILD_VERSION := "latest"
endif

ifndef DOCKER_IMAGE_NAME
	DOCKER_IMAGE_NAME := "black-oak"
endif

ifndef DOCKER_CACHE_IMAGE
	DOCKER_CACHE_IMAGE := $(DOCKER_IMAGE_NAME)-$(BUILD_VERSION).tar
endif

MAKEFLAGS += --silent

docker-build:
	docker build -t $(DOCKER_IMAGE_NAME):$(BUILD_VERSION) .

# saves docker image to disk
docker-save:
	docker save $(DOCKER_IMAGE_NAME):$(BUILD_VERSION) > $(DOCKER_CACHE_IMAGE)

# load saved image
docker-load:
	docker load < $(DOCKER_CACHE_IMAGE)

# runs the container
docker-run: docker-build
	docker run --rm -it $(DOCKER_IMAGE_NAME):$(BUILD_VERSION) ./bin/run_ohlcv_data_fetcher.sh config.toml

# runs container with mounted ./data directory
docker-run-with-mountpoint: docker-build
	docker run -it -v $(PWD)/data/:/usr/src/app/data/ $(DOCKER_IMAGE_NAME):$(BUILD_VERSION) ./bin/run_ohlcv_data_fetcher.sh config.toml

# unit tests with docker cache
docker-test-from-cache: docker-load
	docker run --rm $(DOCKER_IMAGE_NAME):$(BUILD_VERSION) python -m pytest

# unit tests
docker-test: docker-build
	docker run --rm $(DOCKER_IMAGE_NAME):$(BUILD_VERSION) python -m pytest

.PHONY: docker-build
.PHONY: docker-save
.PHONY: docker-load
.PHONY: docker-run
.PHONY: docker-run-with-mountpoint
.PHONY: docker-test-from-cache
.PHONY: docker-test

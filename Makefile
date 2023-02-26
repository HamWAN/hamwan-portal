IMAGE := hamwan-portal
PYTHON_VERSION ?= 2.7
DOCKER_RUNNER := docker run --rm -v $(shell pwd):/app $(IMAGE)

docker:
	docker build --build-arg PYTHON_VERSION=$(PYTHON_VERSION) -t $(IMAGE) .

test:
	$(DOCKER_RUNNER) manage.py test -v3

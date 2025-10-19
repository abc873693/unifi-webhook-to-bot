APP := unifi-webhook-to-bot
VERSION := latest

build:
	docker build -t $(APP) . --no-cache

save:
	docker save $(APP):$(VERSION)  -o $(APP)-image.tar
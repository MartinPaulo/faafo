#!/bin/sh

faafo-producer \
    --amqp-url amqp://tutorial:secretsecret@service:5672/ \
    --api-url http://api:5000 \
    --debug --verbose

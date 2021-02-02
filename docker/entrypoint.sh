#!/bin/bash
set -e


echo "Wait for PostgreSQL to start..."
while ! pg_isready -h db -U ckan; do
    sleep 1;
done
echo "PostgreSQL started"

echo "Wait for Solr to start..."
while ! curl -s "http://solr:8983/solr/ckan/admin/ping" | grep -q OK; do
  sleep 1;
done
echo "Solr started"

echo "Wait for Redis to start..."
while ! echo -e "PING" | nc -w 1 redis 6379 | grep -q "+PONG"; do
  sleep 1;
done
echo "Redis started"

echo "Wait for Elasticsearch to start..."
while ! curl -s "http://elasticsearch:9200/_cluster/health" | grep -q green; do
  sleep 1;
done
echo "Elasticsearch started"

echo "Wait for MongoDB to start..."
while ! nc -z mongodb 27017; do
  sleep 1;
done
echo "MongoDB started"


echo "All services up, running command"

exec "$@"

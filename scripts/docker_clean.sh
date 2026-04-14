#!/usr/bin/env bash

# Stops everything and removes orphaned containers
docker compose down --remove-orphans

# (Optional) Remove the images to save disk space
docker rmi rmus-server rmus-db

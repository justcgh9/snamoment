#!/bin/sh

timestamp=$(date +%Y%m%d%H%M%S)
export PGPASSWORD="sna"

pg_dump -h localhost -p 5432 -U postgres > backup_${timestamp}.sql

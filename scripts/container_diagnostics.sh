#!/bin/sh

echo "==== CONTAINER: $(hostname) ===="

echo "\n==== ENVIRONMENT VARIABLES ===="
printenv

echo "\n==== NETWORK INTERFACES & OPEN PORTS ===="
if command -v netstat >/dev/null 2>&1; then
  netstat -tuln
elif command -v ss >/dev/null 2>&1; then
  ss -tuln
else
  echo "Neither netstat nor ss found"
fi

echo "\n==== REDIS CONNECTIVITY TEST ===="
if command -v redis-cli >/dev/null 2>&1; then
  redis-cli -h 127.0.0.1 ping || echo "Redis not reachable on 127.0.0.1"
else
  echo "redis-cli not installed"
fi

echo "\n==== POSTGRES CONNECTIVITY TEST ===="
if command -v psql >/dev/null 2>&1; then
  PGUSER=${POSTGRES_USER:-postgres}
  PGPASSWORD=${POSTGRES_PASSWORD:-password}
  PGDATABASE=${POSTGRES_DB:-postgres}
  PGHOST=${POSTGRES_HOST:-127.0.0.1}
  PGPORT=${POSTGRES_PORT:-5432}
  echo "Attempting connection to $PGUSER@$PGHOST:$PGPORT/$PGDATABASE"
  PGPASSWORD=$PGPASSWORD psql -h $PGHOST -U $PGUSER -d $PGDATABASE -c '\l' || echo "Postgres not reachable on $PGHOST"
else
  echo "psql not installed"
fi

echo "\n==== FRONTEND/WEB SERVER CONNECTIVITY TEST ===="
WEB_PORT=${WEB_PORT:-8080}
if command -v curl >/dev/null 2>&1; then
  curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:$WEB_PORT/ || echo "Web server not reachable on 127.0.0.1:$WEB_PORT"
else
  echo "curl not installed"
fi

echo "\n==== RECENT LOGS (if available) ===="
if [ -f /var/log/app.log ]; then
  tail -n 20 /var/log/app.log
else
  echo "No /var/log/app.log file found. Check your app log location."
fi

echo "\n==== END OF DIAGNOSTICS ===="
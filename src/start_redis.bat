@echo off
cd /d C:\Users\My-PC\Music

echo Starting Redis Server...
start "" redis-server.exe redis.windows.conf

exit
#!/bin/bash
for i in {0..600}
do
  _ip="$(hostname -I)"
  if [ -n "$_ip" ]; then
    break
  fi
  sleep 1
done
if [ -z "$_ip" ]; then
  ip="timeout"
fi
touch /boot/lastip.log
cp /boot/lastip.log /tmp/lastip.log
echo "[$(date)] $_ip" >> /tmp/lastip.log
tail -n 1000 /tmp/lastip.log > /boot/lastip.log


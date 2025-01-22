#!/bin/bash

# Clear the contents of the file
cat /dev/null >cloudflare_ips.conf

# Fetch and append IPv4 addresses
curl -s https://www.cloudflare.com/ips-v4 | while read -r ip; do
    echo "$ip    1;" >>cloudflare_ips.conf
done

# Fetch and append IPv6 addresses
curl -s https://www.cloudflare.com/ips-v6 | while read -r ip; do
    echo "$ip    1;" >>cloudflare_ips.conf
done

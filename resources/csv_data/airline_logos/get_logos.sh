#/usr/bin/env zsh

while read -r airline; do
    curl -O "https://www.gstatic.com/flights/airline_logos/70px/$airline.png" || true
done <"airlines.csv"
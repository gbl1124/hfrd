#!/bin/bash
SECONDS=0

while (( $SECONDS < 600 ));
do
    if (( $SECONDS > 50 )); then
      echo "Waiting $SECONDS for pod ${NAME} to start completion."
      break
    fi
    sleep 3
done

if [ $SECONDS -ge 600 ]
then
    echo "Timed out waiting for ${NAME} to come up"
    exit 1
fi


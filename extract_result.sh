#! /usr/bin/env bash

set -o nounset
set -o pipefail
set -o errexit

data=''

for file in "$@"; do
    data+=$(echo -e $(cat $file | grep -w 'Not solved' | sed 's/ /\\n/g') | tail -n +4)","
done

echo $data | sed 's/.$//'
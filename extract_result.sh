#! /usr/bin/env bash

set -o nounset
set -o pipefail
set -o errexit

# data=''

# for file in "$@"; do
#     data+=$(echo -e $(cat $file | grep -w 'Not solved' | sed 's/ /\\n/g') | tail -n +4)","
# done

# echo $data | sed 's/.$//'

rm unsuccessful*.txt

echo -e $(cat result_first.txt | grep -w 'Not solved' | sed 's/ /\\n/g') | tail -n +4 > unsuccessful_first.txt

echo -e $(cat result_second.txt | grep -w 'Not solved' | sed 's/ /\\n/g') | tail -n +4 > unsuccessful_second.txt

echo -e $(cat result_third.txt | grep -w 'Not solved' | sed 's/ /\\n/g') | tail -n +4 > unsuccessful_third.txt


# echo -e $(echo -e $(cat result_first.txt | grep -w 'Not solved' | sed 's/ /\\n/g') | tail -n +4 | sed 's/,/\\n/g') | wc -w

# echo -e $(cat unsuccessful_first.txt | sed 's/,/\\n/g') | wc -w

# echo -e $(echo -e $(cat result_second.txt | grep -w 'Not solved' | sed 's/ /\\n/g') | tail -n +4 | sed 's/,/\\n/g') | wc -w

# echo -e $(cat unsuccessful_second.txt | sed 's/,/\\n/g') | wc -w

# echo -e $(echo -e $(cat result_third.txt | grep -w 'Not solved' | sed 's/ /\\n/g') | tail -n +4 | sed 's/,/\\n/g') | wc -w

# echo -e $(cat unsuccessful_third.txt | sed 's/,/\\n/g') | wc -w
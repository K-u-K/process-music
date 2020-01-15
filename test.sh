set -e

for midi in examples/*.mid
do 
    python3 -O process_music/process_music.py ${midi}
done
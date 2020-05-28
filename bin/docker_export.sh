docker save $(docker images -q) | pigz > mydockersimages.tar.gz

docker images | sed '1d' | awk '{print $1 " " $2 " " $3}' > mydockersimages.list

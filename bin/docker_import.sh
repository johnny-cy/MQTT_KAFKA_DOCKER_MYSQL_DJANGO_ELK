unpigz -c mydockersimages.tar.gz | docker load

while read REPOSITORY TAG IMAGE_ID
do
    echo "== Tagging $REPOSITORY $TAG $IMAGE_ID =="
    docker tag "$IMAGE_ID" "$REPOSITORY:$TAG"
done < mydockersimages.list

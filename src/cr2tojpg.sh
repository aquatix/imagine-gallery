#!/bin/bash
if [ -n "$1" ] && [ -n "$2" ]
then
	newname=$(echo $(basename "$1" ".CR2")_small.jpg); dcraw -c -w -W -v -h "$1" | cjpeg -quality 95 -optimize -progressive > "$2/$newname"; exiftool -overwrite_original -tagsFromFile "$1" "$2/$newname"
else
	echo "cr2tojpg.sh origfile.CR2 destinationdir"
fi

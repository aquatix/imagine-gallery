#!/bin/bash
for i in *.CR2; do newname=$(echo $(basename "$i" ".CR2").jpg); dcraw -c -w -W -v -h "$i" | cjpeg -quality 95 -optimize -progressive > "$newname"; exiftool -overwrite_original -tagsFromFile "$i" "$newname"; done

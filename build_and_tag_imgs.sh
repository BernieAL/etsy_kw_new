#!/bin/sh
"""

script will find dockerfiles in project dir
for each docker file 
it will build the image and tag it - using same name
it will then deploy images to ecr

"""



#get dir of current script
#dir to search
"."

#filename to search for
filename="docker-compose.yml"

#use find to search for the file
found_file=$(find "$search_dir" -type f -name "$filename")


#check if file was found
if [[ -n "$found_file" ]]; then
    echo "File found: $found_file"
else
    echo "File not found."

fi


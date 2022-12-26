set +e
# git diff --no-commit-id --name-only --diff-filter=A -M100% HEAD^ HEAD :'^bq_metadata/[^/]*'
# ':!table'
ADDED_FILE_LIST=($(git diff --no-commit-id --name-only --diff-filter=A -M100% HEAD^ HEAD 'bq_metadata/**/*.json' 'bq_metadata/**/*.sql'))
DELETED_FILE_LIST=($(git diff --no-commit-id --name-only --diff-filter=D -M100% HEAD^ HEAD 'bq_metadata/**/*.json' 'bq_metadata/**/*.sql'))
UPDATED_FILE_LIST=($(git diff --no-commit-id --name-only --diff-filter=M HEAD^ HEAD 'bq_metadata/**/*.json' 'bq_metadata/**/*.sql'))

FAILED=0
cd $CI_PROJECT_DIR

export PROJECT_ROOT=/app
export GOOGLE_APPLICATION_CREDENTIALS=${PROJECT_ROOT}/credentials.json

source /venv/bin/activate

#Added
count=0
for file in ${ADDED_FILE_LIST[*]}; do 
    new_file="creation,"$file
    
    if [[ "$file" == *"/views/"* ]]; then
        new_file="view,"$new_file
    elif [[ "$file" == *"/tables/"* ]]; then
        new_file="table,"$new_file
    else new_file="dataset,"$new_file
    fi
    ADDED_FILE_LIST[$count]=$new_file
    count=$((count + 1)) 
done

IFS=$'\n' ADDED_FILE_LIST=($(sort <<<"${ADDED_FILE_LIST[*]}"))
unset IFS

#Updated
count=0
for file in ${UPDATED_FILE_LIST[*]}; do 
    new_file="update,"$file
    
    if [[ "$file" == *"/views/"* ]]; then
        new_file="view,"$new_file
    elif [[ "$file" == *"/tables/"* ]]; then
        new_file="table,"$new_file
    else new_file="dataset,"$new_file
    fi
    UPDATED_FILE_LIST[$count]=$new_file
    count=$((count + 1)) 
done

IFS=$'\n' UPDATED_FILE_LIST=($(sort <<<"${UPDATED_FILE_LIST[*]}"))
unset IFS

#Deleted
count=0
for file in ${DELETED_FILE_LIST[*]}; do 
    new_file="deletion,"$file
    
    if [[ "$file" == *"/views/"* ]]; then
        new_file="view,"$new_file
    elif [[ "$file" == *"/tables/"* ]]; then
        new_file="table,"$new_file
    else new_file="dataset,"$new_file
    fi
    DELETED_FILE_LIST[$count]=$new_file
    count=$((count + 1)) 
done

ALL_LIST=( ${ADDED_FILE_LIST[*]} ${UPDATED_FILE_LIST[*]} ${DELETED_FILE_LIST[*]} )

for file in "${ALL_LIST[@]}"
do
    IFS=',' read -r -a file_array <<< "$file"
    
    if [[ "${file_array[1]}" == "deletion" && "${file_array[0]}" != "view" ]]; then
      deleted_content=$(git show HEAD~1:${file_array[2]})

      cat >./temp.json <<EOF
      $deleted_content
EOF
      echo python "$PROJECT_ROOT"/main.py -t ${file_array[0]} -e deletion -f temp.json
      python "$PROJECT_ROOT"/main.py -t ${file_array[0]} -e deletion -f temp.json
  
    elif [[ "${file_array[1]}" == "deletion" && "${file_array[0]}" == "view" ]]; then
    IFS='/' read -r -a view_array <<< "${file_array[2]}"
    
    view_name=${view_array[1]}:${view_array[2]}.${view_array[4]}
    echo python "$PROJECT_ROOT"/main.py -t ${file_array[0]} -e deletion -f $view_name
    python "$PROJECT_ROOT"/main.py -t ${file_array[0]} -e deletion -f $view_name

    else echo python "$PROJECT_ROOT"/main.py -t ${file_array[0]} -e ${file_array[1]} -f ${file_array[2]}
    python "$PROJECT_ROOT"/main.py -t ${file_array[0]} -e ${file_array[1]} -f ${file_array[2]}
    fi
done

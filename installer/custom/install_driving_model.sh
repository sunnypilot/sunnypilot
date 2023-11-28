export MODEL_DIR=/data/media/0/models
export MODEL_LOCATION=$(cat /data/params/d/ModelUrl)
export MODEL_LOCATION_TEXT=$(cat /data/params/d/ModelName)

export MODEL_FILE_NAME="supercombo-${MODEL_LOCATION_TEXT}.thneed"
export MODEL_FILE=${MODEL_DIR}/${MODEL_FILE_NAME}

cd $MODEL_DIR

wget -O ${MODEL_FILE_NAME} ${MODEL_LOCATION}

if [[ "$?" != 0 ]]; then
  echo "Error downloading driving model file ${MODEL_LOCATION_TEXT}"
else
  echo "Successfully downloaded driving model file ${MODEL_LOCATION_TEXT}"
fi

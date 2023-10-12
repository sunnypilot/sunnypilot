export OSM_DIR=/data/media/0/osm
export DB_DIR=${OSM_DIR}/db

export OSM_LOCATION=$(cat /data/params/d/OsmLocationUrl)

export OSM_LOCATION_TEXT=$(cat /data/params/d/OsmLocationName)

export XZ_MAP_FILE_NAME=${OSM_LOCATION_TEXT}.tar.xz
export XZ_MAP_FILE=${OSM_DIR}/${XZ_MAP_FILE_NAME}

# WD
cd $OSM_DIR

# Remove legacy compressed map file if existing
rm -rf $XZ_MAP_FILE

# Download map file
wget -O ${XZ_MAP_FILE_NAME} ${OSM_LOCATION}

if [[ "$?" != 0 ]]; then
  echo "Error downloading map file"
else
  echo "Successfully downloaded map file"
  # Remove current db dir if existing
  rm -rf $DB_DIR
  if [ -d ${OSM_DIR}/${OSM_LOCATION_TEXT} ]; then
    rm -rf ${OSM_DIR}/${OSM_LOCATION_TEXT}
  fi
  # Decompressing
  tar -vxf ${XZ_MAP_FILE_NAME}
  mv ${OSM_LOCATION_TEXT} db

  # Remove compressed map files after expanding
  rm -rf $XZ_MAP_FILE
fi

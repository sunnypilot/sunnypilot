# OSM Installation instructions:
# https://wiki.openstreetmap.org/wiki/Overpass_API/Installation

# Install expat. All other needed libraries are already installed.
# g++ make expat libexpat1-dev zlib1g-dev
#sudo apt-get update
#sudo apt-get install expat

# Add required path variables to environment
export OSM_ROOT=/data/media/0/osm
export OSM_VERSION=0.7.57
export GZ_FILE=osm-3s_v${OSM_VERSION}.tar.xz
export OSM_DIR=${OSM_ROOT}/v${OSM_VERSION}
# export DB_DIR=/data/osm/db/

# Download and extract overpass library

if [ ! -d ${OSM_ROOT} ]; then
  mkdir -p ${OSM_ROOT}
fi
tar -vxf /data/openpilot/selfdrive/mapd/assets/${GZ_FILE} -C ${OSM_ROOT}

# Configure and install overpass
#cd $(ls | grep $SOURCE_FILE_ROOT\.[0-9]*)
#cd osm-3s_v0.7.56
#./configure CXXFLAGS="-O2" --prefix=$EXEC_DIR
#make install

# Remove source files after installation
#cd ..
if [ -d ${OSM_DIR} ]; then
  rm -rf ${OSM_DIR}
fi

mv ${OSM_ROOT}/osm-3s_v${OSM_VERSION} ${OSM_ROOT}/v${OSM_VERSION}

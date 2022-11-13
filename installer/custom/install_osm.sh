# OSM Installation instructions:
# https://wiki.openstreetmap.org/wiki/Overpass_API/Installation

# Install expat. All other needed libraries are already installed.
# g++ make expat libexpat1-dev zlib1g-dev
#sudo apt-get update
#sudo apt-get install expat

# Add required path variables to environment
export EXEC_DIR=/data/media/0/osm/v0.7.57/
export SOURCE_FILE_ROOT=osm-3s_v0.7.57
export GZ_FILE=${SOURCE_FILE_ROOT}.tar.xz
# export DB_DIR=/data/osm/db/

# Download and extract overpass library
cd /data/media/0/
if [ ! -d /data/media/0/osm ]; then
  mkdir osm
fi
cd /data/media/0/osm
#wget http://dev.overpass-api.de/releases/$GZ_FILE
cp -f /data/openpilot/selfdrive/mapd/assets/$GZ_FILE .
tar -vxf $GZ_FILE

# Configure and install overpass
#cd $(ls | grep $SOURCE_FILE_ROOT\.[0-9]*)
#cd osm-3s_v0.7.56
#./configure CXXFLAGS="-O2" --prefix=$EXEC_DIR
#make install

# Remove source files after installation
#cd ..
if [ -d ${EXEC_DIR} ]; then
  rm -rf ${EXEC_DIR}
fi
mv osm-3s_v0.7.57 v0.7.57

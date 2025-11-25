#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
ROOT="$(cd $DIR/../ && pwd)"
ARCH=$(uname -m)

# homebrew update is slow
export HOMEBREW_NO_AUTO_UPDATE=1

if [[ $SHELL == "/bin/zsh" ]]; then
  RC_FILE="$HOME/.zshrc"
elif [[ $SHELL == "/bin/bash" ]]; then
  RC_FILE="$HOME/.bash_profile"
fi

# Install brew if required
if [[ $(command -v brew) == "" ]]; then
  echo "Installing Homebrew"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  echo "[ ] installed brew t=$SECONDS"

  # make brew available now
  if [[ $ARCH == "x86_64" ]]; then
    echo 'eval "$(/usr/local/bin/brew shellenv)"' >> $RC_FILE
    eval "$(/usr/local/bin/brew shellenv)"
  else
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> $RC_FILE
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
else
    brew up
fi

brew bundle --file=- <<-EOS
brew "git-lfs"
brew "capnp"
brew "coreutils"
brew "eigen"
brew "ffmpeg"
brew "glfw"
brew "libusb"
brew "libtool"
brew "llvm"
brew "openssl@3.0"
brew "qt@5"
brew "zeromq"
brew "portaudio"
brew "gcc@13"
EOS

# TODO: revert back to using 'cask "gcc-arm-embedded"' when ARM fixes https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads for 14.3
curl -L "https://raw.githubusercontent.com/Homebrew/homebrew-cask/c0149383c504eda206cdb9988c10b561c5d55dfe/Casks/g/gcc-arm-embedded.rb" > gcc-arm-embedded.rb && brew install --cask gcc-arm-embedded.rb
rm -f gcc-arm-embedded.rb

echo "[ ] finished brew install t=$SECONDS"

BREW_PREFIX=$(brew --prefix)

# archive backend tools for pip dependencies
export LDFLAGS="$LDFLAGS -L${BREW_PREFIX}/opt/zlib/lib"
export LDFLAGS="$LDFLAGS -L${BREW_PREFIX}/opt/bzip2/lib"
export CPPFLAGS="$CPPFLAGS -I${BREW_PREFIX}/opt/zlib/include"
export CPPFLAGS="$CPPFLAGS -I${BREW_PREFIX}/opt/bzip2/include"

# pycurl curl/openssl backend dependencies
export LDFLAGS="$LDFLAGS -L${BREW_PREFIX}/opt/openssl@3/lib"
export CPPFLAGS="$CPPFLAGS -I${BREW_PREFIX}/opt/openssl@3/include"
export PYCURL_CURL_CONFIG=/usr/bin/curl-config
export PYCURL_SSL_LIBRARY=openssl

# install python dependencies
$DIR/install_python_dependencies.sh
echo "[ ] installed python dependencies t=$SECONDS"

# brew does not link qt5 by default
# check if qt5 can be linked, if not, prompt the user to link it
QT_BIN_LOCATION="$(command -v lupdate || :)"
if [ -n "$QT_BIN_LOCATION" ]; then
  # if qt6 is linked, prompt the user to unlink it and link the right version
  QT_BIN_VERSION="$(lupdate -version | awk '{print $NF}')"
  if [[ ! "$QT_BIN_VERSION" =~ 5\.[0-9]+\.[0-9]+ ]]; then
    echo
    echo "lupdate/lrelease available at PATH is $QT_BIN_VERSION"
    if [[ "$QT_BIN_LOCATION" == "$(brew --prefix)/"* ]]; then
      echo "Run the following command to link qt5:"
      echo "brew unlink qt@6 && brew link qt@5"
    else
      echo "Remove conflicting qt entries from PATH and run the following command to link qt5:"
      echo "brew link qt@5"
    fi
  fi
else
  brew link qt@5
fi

echo
echo "----   OPENPILOT SETUP DONE   ----"
echo "Open a new shell or configure your active shell env by running:"
echo "source $RC_FILE"

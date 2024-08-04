#!/usr/bin/env bash
mv .lfsconfig .lfsconfig.bak
mv .lfsconfig-comma .lfsconfig
git lfs fetch --all; git lfs pull
mv .lfsconfig .lfsconfig-comma
mv .lfsconfig.bak .lfsconfig
git lfs fetch --all; git lfs push --all origin

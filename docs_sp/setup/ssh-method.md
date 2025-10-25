# SSH Method

If you are looking to install sunnypilot via SSH, run the following commands in an SSH terminal after connecting to your comma 3/3X:

1. Navigate to `data` directory
    ```sh 
    cd /data
    rm -rf openpilot
    ```

2. Clone sunnypilot

    !!! example ""
        `staging` branch is used in this step as an example.
    ```sh
    git clone -b staging --recurse-submodules https://github.com/sunnypilot/sunnypilot.git openpilot
    ```

3. Git LFS
    ```sh
    cd openpilot
    git lfs pull
    ```

4. Reboot
    ```sh
    sudo reboot
    ```

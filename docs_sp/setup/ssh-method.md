# SSH Method

If you are looking to install sunnypilot via SSH, run the following commands in an SSH terminal after connecting to your comma 3/3X:

1. Navigate to `data` directory
    ```sh 
    cd /data
    ```

2. Clone sunnypilot

    !!! example ""
        `release-c3` branch is used in this step as an example.
    ```sh
    git clone -b release-c3 --recurse-submodules https://github.com/sunnyhaibin/openpilot.git 
    ```

3. Git LFS
    ```sh
    git lfs pull
    ```

4. Reboot
    ```sh
    sudo reboot
    ```

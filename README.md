# FallDetector

This project is to play the alarm whenever detecting people falling in an edge application using OpenVino-2020.1.
This app perform single person fall detection using OpenVINO's 
[human-pose-estimation-0001](https://docs.openvinotoolkit.org/latest/_models_intel_human_pose_estimation_0001_description_human_pose_estimation_0001.html) 
pre-trained model.
To detect falls, the app uses the coordinates of the head(nose, eyes and ears), neck and shoulders positions 
in a frame-by-frame comparison to determine when the person is falling.

## Structure

- src

    The main source code for detection of human falling and playing the alarm

- utils

    * The pre-trained OpenVino Pose detection model
    * The source code for folder and file management

- app

    The main execution file

- requirements

    All the dependencies for this project

- settings

    Several settings including the alarm text

## Installation

- Environment

    Ubuntu 18.04, Python 3.6

- OpenVino Installation

    * Please run the following commands in the terminal.
    ```        
        sudo curl -o GPG-PUB-KEY-INTEL-SW-PRODUCTS-2020.PUB https://apt.repos.intel.com/openvino/2020/GPG-PUB-KEY-INTEL-OPENVINO-2020
        sudo apt-key add GPG-PUB-KEY-INTEL-SW-PRODUCTS-2020.PUB
        sudo su -c "echo 'deb https://apt.repos.intel.com/openvino/2020 all main' > /etc/apt/sources.list.d/intel-openvino-2020.list"
        sudo apt-get update
        sudo apt-get install -y --no-install-recommends intel-openvino-dev-ubuntu18-2020.1.023 ocl-icd-opencl-dev
        cd /opt/intel/openvino/install_dependencies
        sudo -E ./install_openvino_dependencies.sh        
        cd /opt/intel/openvino/deployment_tools/model_optimizer/install_prerequisites
        sudo ./install_prerequisites.sh        
    ```
    * Please add the following command line into /home/{user}/.bashrc.
    ```
        vi /home/{user}/.bashrc        
    ```
    ```
        source /opt/intel/openvino/bin/setupvars.sh
    ```

- Dependency Installation

    Please run the following command in the terminal.
    ```
        sudo apt install libespeak1
        sudo apt-get install libboost-dev libboost-log-dev
        pip3 install -r requirements.txt         
    ```
 
## Execution

- Please set ALARM_TEXT in settings file with the alarm text as you want and connect web camera to the pc.

- Please run the following command in the terminal.

    ```
        python3 app.py
    ```

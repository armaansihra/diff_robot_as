import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

import xacro


def generate_launch_description():

    roboxacname = "armaan_robo"
    nameofpkg = "arma_rob"

    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true'
    )

    
    modelfilerelpath = "model/allfile.xacro"
    modelfilepath = os.path.join(
        get_package_share_directory(nameofpkg),
        modelfilerelpath
    )

    robotdesc = xacro.process_file(modelfilepath).toxml()

    
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            )
        ),
        launch_arguments={
            'gz_args': '-r -v 4 empty.sdf',
            'on_exit_shutdown': 'true'
        }.items()
    )

    spawn_model = Node(
        package="ros_gz_sim",
        executable='create',
        arguments=[
            '-name', roboxacname,
            '-string', robotdesc,
            '-x', '0',
            '-y', '0',
            '-z', '0.3'
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    bridge_params = os.path.join(
        get_package_share_directory(nameofpkg),
        'parameters',
        'bridge_parameters.yaml'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
    )


    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robotdesc,
            'use_sim_time': use_sim_time
        }]
    )


    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )


    ld = LaunchDescription()

    ld.add_action(declare_sim_time)
    ld.add_action(gazebo_launch)
    ld.add_action(spawn_model)
    ld.add_action(bridge)
    ld.add_action(rsp)
    ld.add_action(rviz)

    return ld
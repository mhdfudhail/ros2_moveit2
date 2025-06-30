#!/usr/bin/python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler, DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
import xacro
import yaml


def generate_launch_description():
    
    # Gazebo world file:
    genbot_gazebo_world = os.path.join(
        get_package_share_directory('franka_gazebo'),
        'worlds',
        'ware_house_1.world')
    # gazebo launch file:
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']),
                launch_arguments={'world': genbot_gazebo_world}.items(),
             )

    # Genbot Model Description file package:
    genbot_description_path = os.path.join(
        get_package_share_directory('franka_description'))
    # Genbot ROBOT urdf file path:
    xacro_file = os.path.join(genbot_description_path,
                              'urdf',
                              'panda_2.urdf.xacro')
    # Generate ROBOT_DESCRIPTION for Genbot_v3:
    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    robot_description_config = doc.toxml()
    robot_description = {'robot_description': robot_description_config}

    # ROBOT STATE PUBLISHER NODE:
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name="robot_state_publisher",
        output='both',
        parameters=[robot_description]
    )
    # Static TF:
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "world", "base_link"],
    )

    # SPAWN ROBOT TO GAZEBO:
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'panda_2'],
                        output='both')

    # Joint state broadcaster:
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )
    # Joint trajectory Controllers:
    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
    )
    hand_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["hand_controller"],
    )
    diff_cont_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )
   
    # Command-line argument: RVIZ file?
    rviz_arg = DeclareLaunchArgument(
        "rviz_file", default_value="False", description="Load RVIZ file."
    )

    # *** PLANNING CONTEXT *** #
    # Robot description, URDF:
    robot_description_config = xacro.process_file(
        os.path.join(
            get_package_share_directory("franka_description"),
            "urdf",
            "panda_2.urdf.xacro",
        )
    )
    robot_description = {"robot_description": robot_description_config.toxml()}


    return LaunchDescription([
        gazebo, 
        spawn_entity,
        node_robot_state_publisher,
        static_tf,
        RegisterEventHandler(
            OnProcessExit(
                target_action = spawn_entity,
                on_exit = [
                    joint_state_broadcaster_spawner,  
                ]
            )
        ),
        RegisterEventHandler(
            OnProcessExit(
                target_action = joint_state_broadcaster_spawner,
                on_exit = [
                    arm_controller_spawner
                ]
            )
        ),
        RegisterEventHandler(
            OnProcessExit(
                target_action = joint_state_broadcaster_spawner,
                on_exit = [
                    hand_controller_spawner,
                ]
            )
        ),
        RegisterEventHandler(
            OnProcessExit(
                target_action = joint_state_broadcaster_spawner,
                on_exit = [
                    diff_cont_controller_spawner,
                ]
            )
        ),
        
    ])
        
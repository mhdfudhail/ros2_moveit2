from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch.actions import ExecuteProcess
import os

def generate_launch_description():
    # get path to package and urdf
    pkg_description = get_package_share_directory('franka_gazebo')
    urdf_file = os.path.join(pkg_description, "urdf",'franka_gazebo.urdf')
    mesh_pkg_share_dir = os.pathsep+os.path.join(get_package_prefix('franka_description'),'share')

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] +=mesh_pkg_share_dir
    else:
        os.environ['GAZEBO_MODEL_PATH'] =mesh_pkg_share_dir

    with open(urdf_file, 'r') as file:
        urdf_content = file.read()

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{'robot_description': urdf_content}]
    )
    gazebo_bringup = ExecuteProcess(
            cmd=["gazebo", "--verbose", "-s", "libgazebo_ros_factory.so"],
            output="screen"
    )
    spawn_node = Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=["-entity", "panda", "-topic","/robot_description"],
            output="screen"
        )
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=["joint_state_broadcaster"]
    )
    arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=["arm_controller"]
    )
    hand_controller = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=["hand_controller"]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        gazebo_bringup,
        spawn_node,
        joint_state_broadcaster,
        arm_controller,
        hand_controller
    ])

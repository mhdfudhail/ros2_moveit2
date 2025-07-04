
import os
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory, get_package_prefix

def generate_launch_description():

  # Constants for paths to different files and folders
  package_name_description = 'franka_description'
  package_name_gazebo = 'franka_description'

  default_robot_name = 'panda'
  gazebo_launch_file_path = 'launch'
  gazebo_models_path = 'models'
  rviz_config_file_path = 'rviz/'
  urdf_file_path = 'urdf/franka_gazebo.urdf'

  pkg_description = get_package_share_directory('franka_gazebo')
  urdf_file = os.path.join(pkg_description, "urdf",'franka_gazebo.urdf')
  with open(urdf_file, 'r') as file:
        urdf_content = file.read()
  world_file_path = 'worlds/empty_world.world' # Example: 'worlds/house_classic.world', 'worlds/empty_classic.world', 'worlds/small_warehouse_classic.world'

  # Set the path to different files and folders.  
  pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')  
  pkg_share_description = FindPackageShare(package=package_name_description).find(package_name_description)
  pkg_share_gazebo = FindPackageShare(package=package_name_gazebo).find(package_name_gazebo)

  default_rviz_config_path = os.path.join(pkg_share_description, rviz_config_file_path)  
  default_urdf_model_path = os.path.join(pkg_share_gazebo, urdf_file_path)
  gazebo_launch_file_path = os.path.join(pkg_share_gazebo, gazebo_launch_file_path)   
  gazebo_models_path = os.path.join(pkg_share_gazebo, gazebo_models_path)
  world_path = os.path.join(pkg_share_gazebo, world_file_path)
  
  # Launch configuration variables specific to simulation
  headless = LaunchConfiguration('headless')
  robot_name = LaunchConfiguration('robot_name')
  rviz_config_file = LaunchConfiguration('rviz_config_file')
  urdf_model = LaunchConfiguration('urdf_model')
  use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
  use_rviz = LaunchConfiguration('use_rviz')
  use_sim_time = LaunchConfiguration('use_sim_time')
  use_simulator = LaunchConfiguration('use_simulator')
  world = LaunchConfiguration('world')
  
  # Set the default pose
  x = LaunchConfiguration('x')
  y = LaunchConfiguration('y')
  z = LaunchConfiguration('z')
  roll = LaunchConfiguration('roll')
  pitch = LaunchConfiguration('pitch')
  yaw = LaunchConfiguration('yaw')
  
  # Declare the launch arguments  
  declare_robot_name_cmd = DeclareLaunchArgument(
    name='robot_name',
    default_value=default_robot_name,
    description='The name for the robot')

  declare_rviz_config_file_cmd = DeclareLaunchArgument(
    name='rviz_config_file',
    default_value=default_rviz_config_path,
    description='Full path to the RVIZ config file to use')

  declare_simulator_cmd = DeclareLaunchArgument(
    name='headless',
    default_value='False',
    description='Display the Gazebo GUI if False, otherwise run in headless mode')

  declare_urdf_model_path_cmd = DeclareLaunchArgument(
    name='urdf_model', 
    default_value=default_urdf_model_path, 
    description='Absolute path to robot urdf file')
    
  declare_use_robot_state_pub_cmd = DeclareLaunchArgument(
    name='use_robot_state_pub',
    default_value='True',
    description='Whether to start the robot state publisher')

  declare_use_rviz_cmd = DeclareLaunchArgument(
    name='use_rviz',
    default_value='True',
    description='Whether to start RVIZ')
    
  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='true',
    description='Use simulation (Gazebo) clock if true')

  declare_use_simulator_cmd = DeclareLaunchArgument(
    name='use_simulator',
    default_value='True',
    description='Whether to start Gazebo')

  declare_world_cmd = DeclareLaunchArgument(
    name='world',
    default_value=world_path,
    description='Full path to the world model file to load')

  declare_x_cmd = DeclareLaunchArgument(
    name='x',
    default_value='0.0',
    description='x component of initial position, meters')

  declare_y_cmd = DeclareLaunchArgument(
    name='y',
    default_value='0.0',
    description='y component of initial position, meters')
    
  declare_z_cmd = DeclareLaunchArgument(
    name='z',
    default_value='0.05', # 0.05 for house_classic.world and empty_classic.world, 0.2 for small_warehouse_classic.world
    description='z component of initial position, meters')
    
  declare_roll_cmd = DeclareLaunchArgument(
    name='roll',
    default_value='0.0',
    description='roll angle of initial orientation, radians')

  declare_pitch_cmd = DeclareLaunchArgument(
    name='pitch',
    default_value='0.0',
    description='pitch angle of initial orientation, radians')

  declare_yaw_cmd = DeclareLaunchArgument(
    name='yaw',
    default_value='0.0',
    description='yaw angle of initial orientation, radians')
    
  # Specify the actions

  set_env_vars_resources = AppendEnvironmentVariable(
    'GAZEBO_MODEL_PATH',
    gazebo_models_path)
  
  # Launch arm controller
  start_arm_controller_cmd = Node(
    package="controller_manager",
    executable="spawner",
    arguments=[
      "arm_controller",
      "--controller-manager",
      "/controller_manager"
    ]
  )  

  # Launch gripper controller
  start_hand_controller_cmd = Node(
    package="controller_manager",
    executable="spawner",
    arguments=[
      "hand_controller",
      "--controller-manager",
      "/controller_manager"
    ]
  )  
  
  # Start Gazebo server
  start_gazebo_server_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
    condition=IfCondition(use_simulator),
    launch_arguments={'world': world}.items())

  # Start Gazebo client    
  start_gazebo_client_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')),
    condition=IfCondition(PythonExpression([use_simulator, ' and not ', headless])))

  # Launch joint state broadcaster
  start_joint_state_broadcaster_cmd = Node(
    package="controller_manager",
    executable="spawner",
    arguments=[
      "joint_state_broadcaster",
      "--controller-manager",
      "/controller_manager"
    ]
  )  
    
  # Subscribe to the joint states of the robot, and publish the 3D pose of each link.
  # robot_description_content = ParameterValue(Command(['xacro ', urdf_model]), value_type=None)
  robot_description_content = ParameterValue(urdf_content, value_type=str)
  start_robot_state_publisher_cmd = Node(
    condition=IfCondition(use_robot_state_pub),
    package='robot_state_publisher',
    executable='robot_state_publisher',
    name='robot_state_publisher',
    output='screen',
    parameters=[{
      'use_sim_time': use_sim_time,
      'robot_description': robot_description_content}])

  # Launch RViz
  start_rviz_cmd = Node(
    condition=IfCondition(use_rviz),
    package='rviz2',
    executable='rviz2',
    name='rviz2',
    output='screen',
    arguments=['-d', rviz_config_file])  
    
  # Spawn the robot
  start_gazebo_ros_spawner_cmd = Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    arguments=[
      '-entity', robot_name,
      '-topic', "robot_description", 
      '-x', x,
      '-y', y,
      '-z', z,
      '-R', roll,
      '-P', pitch,
      '-Y', yaw
      ],
    output='screen')  
    
  # Create the launch description and populate
  ld = LaunchDescription()

  # Declare the launch options
  ld.add_action(declare_robot_name_cmd)
  # ld.add_action(declare_rviz_config_file_cmd)
  ld.add_action(declare_simulator_cmd)
  ld.add_action(declare_urdf_model_path_cmd)
  ld.add_action(declare_use_robot_state_pub_cmd)  
  # ld.add_action(declare_use_rviz_cmd) 
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_use_simulator_cmd)
  ld.add_action(declare_world_cmd)

  ld.add_action(declare_x_cmd)
  ld.add_action(declare_y_cmd)
  ld.add_action(declare_z_cmd)
  ld.add_action(declare_roll_cmd)
  ld.add_action(declare_pitch_cmd)
  ld.add_action(declare_yaw_cmd)  

  # Add any actions
  ld.add_action(set_env_vars_resources)
  ld.add_action(start_arm_controller_cmd) 
  ld.add_action(start_gazebo_server_cmd)
  ld.add_action(start_gazebo_client_cmd)
  ld.add_action(start_hand_controller_cmd) 
  ld.add_action(start_joint_state_broadcaster_cmd)
  ld.add_action(start_robot_state_publisher_cmd)
  # ld.add_action(start_rviz_cmd)  
  ld.add_action(start_gazebo_ros_spawner_cmd)

  return ld




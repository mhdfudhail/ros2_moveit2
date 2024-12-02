import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import roboticstoolbox as rtb
from spatialmath.base import *
from spatialmath import SE3
import sys

class JointController(Node):
    def __init__(self, x=None,y=None,z=None):
        super().__init__("joint_controller")
        topic_name = "/joint_trajectory_controller/joint_trajectory"
        self.trajectory_publisher = self.create_publisher(JointTrajectory, topic_name,10)
        self.timer = self.create_timer(1, self.timer_callback) 
        self.joints = ["panda_joint1", "panda_joint2", "panda_joint3", 
                      "panda_joint4", "panda_joint5", "panda_joint6", 
                      "panda_joint7","panda_finger_joint1"]
        self.goal_positions = self.calculate_goal_joint_pose(x,y,z)

    def calculate_goal_joint_pose(self, x, y, z):
        point = SE3(x,y,z)
        robotic_arm = rtb.models.URDF.Panda()
        ik_joints = robotic_arm.ikine_LM(point)
        return ik_joints.q.tolist()+[0.032]

    def timer_callback(self):
        trajectory_msg = JointTrajectory()
        trajectory_msg.joint_names = self.joints
        point = JointTrajectoryPoint()
        point.positions = self.goal_positions
        point.time_from_start = Duration(sec=2)
        trajectory_msg.points.append(point)
        self.trajectory_publisher.publish(trajectory_msg)


def main(args=None):
    rclpy.init(args=args)
    if len(sys.argv)==4:
        x = float(sys.argv[1])
        y = float(sys.argv[2])
        z = float(sys.argv[3])
    else:
        x=y=z=None
    trajectory_publisher_node = JointController(x, y, z)
    rclpy.spin(trajectory_publisher_node)
    trajectory_publisher_node.destroy_node()
    rclpy.shutdown()



if __name__=="__main__":
    main()
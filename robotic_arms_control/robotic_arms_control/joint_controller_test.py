import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint



class JointController(Node):
    def __init__(self):
        super().__init__("joint_controller")
        topic_name = "/joint_trajectory_controller/joint_trajectory"
        self.trajectory_publisher = self.create_publisher(JointTrajectory, topic_name,10)
        self.timer = self.create_timer(1, self.timer_callback) 
        self.joints = ["panda_joint1", "panda_joint2", "panda_joint3", 
                      "panda_joint4", "panda_joint5", "panda_joint6", 
                      "panda_joint7","panda_finger_joint1"]
        self.goal_positions = [-2.453, -1.531, -1.704, -1.478, 1.623, 1.442, -1.375, 0.0]


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
    trajectory_publisher_node = JointController()
    rclpy.spin(trajectory_publisher_node)
    trajectory_publisher_node.destroy_node()
    rclpy.shutdown()



if __name__=="__main__":
    main()
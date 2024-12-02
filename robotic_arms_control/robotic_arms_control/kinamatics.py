import roboticstoolbox as rtb
from spatialmath.base import *
from spatialmath import SE3
import numpy as np

robotic_arm = rtb.models.URDF.Panda()

# print(robotic_arm)

# forward kinematics
fk_joints = robotic_arm.fkine(robotic_arm.qz)
print(fk_joints)

# inverse kinematics
point = SE3(0.0, 0.7, 0.5)
ik_joints = robotic_arm.ikine_LM(point)
# print(ik_joints)
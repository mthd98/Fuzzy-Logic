
import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformRegistration
from rclpy.qos import QoSProfile, ReliabilityPolicy
from fuzzy import Fuzzy
import json
import numpy as np 




with open("/mnt/mm24268/m-drive/Robotics Lab/Week 04 Fuzzy logic/turtlebot3_ws/src/right_edge_ranges.json",'r') as f :
    right_edge_ranges = json.load(f)
    


with open("/mnt/mm24268/m-drive/Robotics Lab/Week 04 Fuzzy logic/turtlebot3_ws/src/obstacle_avoidance_ranges.json",'r') as f :
    obstacle_avoidance_ranges = json.load(f)

right_edge_fuzzy = Fuzzy(right_edge_ranges["inputs"],right_edge_ranges["outputs"],r"/mnt/mm24268/m-drive/Robotics Lab/Week 04 Fuzzy logic/turtlebot3_ws/src/right_edge_rule_table.csv")
obstacle_avoidance_fuzzy = Fuzzy(obstacle_avoidance_ranges["inputs"],obstacle_avoidance_ranges["outputs"],r"/mnt/mm24268/m-drive/Robotics Lab/Week 04 Fuzzy logic/turtlebot3_ws/src/obstacle_avoidance_Rule_Base_Table.csv")


    



mynode_ = None
pub_ = None
regions_ = {
    'right': 0,
    'fright': 0,
    "bright":0,
    'front1': 0,
    'front2': 0,
    'fleft': 0,
    'left': 0,
}
twstmsg_ = None



def range_checker(minimum, value, maximum):
    """Checks if a value is within a given range (inclusive of minimum and maximum).

    Args:
        minimum (float): The lower bound of the range.
        value (float): The value to check.
        maximum (float): The upper bound of the range.

    Returns:
        int: 1 if the value is within the range, 0 otherwise.
    """
    if minimum <= value <= maximum:
        return 1
    else:
        return 0


def action_chosser(right_edge_inputs, obstacle_avoidance_inputs):
    """Determines the action to take based on fuzzy logic rules applied to 
    right edge and obstacle avoidance inputs.

    Args:
        right_edge_inputs (list or array): The fuzzy inputs for the right edge.
        obstacle_avoidance_inputs (list or array): The fuzzy inputs for obstacle avoidance.

    Returns:
        float: The resulting action based on the fuzzy logic rules.
    """
    
    # Initialize the rules dictionary with default values
    rules = {
        "RE": 0,
        "OA": 0
    }
    
    # Apply fuzzy logic to get the results for each input
    right_edge_result = right_edge_fuzzy(right_edge_inputs)
    obstacle_avoidance_result = obstacle_avoidance_fuzzy(obstacle_avoidance_inputs)
    
    # Get the minimum values for right edge and obstacle avoidance inputs
    min_right_edge = np.min(right_edge_inputs)
    min_obstacle_avoidance = np.min(obstacle_avoidance_inputs)
    
    # Use range_checker to determine if the inputs fall within the defined ranges
    rules["RE"] = range_checker(0.3, min_right_edge,1.0)
    rules["OA"] = range_checker(0.0, min_obstacle_avoidance, 0.4)
    right_edge_result[1] = right_edge_result[1]*-1
    # Calculate the weighted sum for determining the action
    numerator = rules["RE"] * np.array(right_edge_result) + rules["OA"] * np.array(obstacle_avoidance_result)
     
    # Calculate the sum of the rules to use as the denominator
    denominator = rules["RE"] + rules["OA"]
    
    # Avoid division by zero, return right edge result
    if denominator == 0 :
        action = right_edge_result

   
    else:
        action = numerator / denominator

    print(rules)
    
    return action

# main function attached to timer callback
def timer_callback():
    global pub_, twstmsg_
    if ( twstmsg_ != None ):
        pub_.publish(twstmsg_)


def clbk_laser(msg):
    global regions_, twstmsg_
    
    regions_ = {
        #LIDAR readings are anti-clockwise
        'front1':  find_nearest (msg.ranges[0:10]),
        'front2':  find_nearest (msg.ranges[350:360]),
        'right':  find_nearest(msg.ranges[265:275]),
        'fright': find_nearest (msg.ranges[310:320]),
        "bright": find_nearest(msg.ranges[210:220]),
        'fleft':  find_nearest (msg.ranges[40:50]),
        'left':   find_nearest (msg.ranges[85:95])
        
    }    
    twstmsg_= movement()

    
# Find nearest point
def find_nearest(list):
    f_list = filter(lambda item: item > 0.0, list)  # exclude zeros
    return min(min(f_list, default=0.999), 0.999)



    

#Basic movement method
def movement():
    #print("here")
    global regions_, mynode_
    regions = regions_
    
    
    
    #create an object of twist class, used to express the linear and angular velocity of the turtlebot 
    msg = Twist()
    right_edge_inputs = np.array([regions["fright"],regions["bright"]])
    print("Min distance in right region: ", right_edge_inputs)
    front= min([regions["front1"],regions["front2"]])
    obstacle_avoidance_inputs = np.array([regions["fright"],front,regions["fleft"]])

    

    action = action_chosser(right_edge_inputs,obstacle_avoidance_inputs)

    
    
     
    

    msg.linear.x = action[0]


    msg.angular.z = action[1]
    print(action)

    return msg
    
      
    
      
        


#used to stop the rosbot
def stop():
    global pub_
    msg = Twist()
    msg.angular.z = 0.0
    msg.linear.x = 0.0
    pub_.publish(msg)


def main():
    global pub_, mynode_

    rclpy.init()
    mynode_ = rclpy.create_node('reading_laser')

    # define qos profile (the subscriber default 'reliability' is not compatible with robot publisher 'best effort')
    qos = QoSProfile(
        depth=10,
        reliability=ReliabilityPolicy.BEST_EFFORT,
    )

    # publisher for twist velocity messages (default qos depth 10)
    pub_ = mynode_.create_publisher(Twist, '/cmd_vel', 10)

    # subscribe to laser topic (with our qos)
    sub = mynode_.create_subscription(LaserScan, '/scan', clbk_laser, qos)

    # Configure timer
    timer_period = 0.2  # seconds 
    timer = mynode_.create_timer(timer_period, timer_callback)

    # Run and handle keyboard interrupt (ctrl-c)
    try:
        rclpy.spin(mynode_)
    except KeyboardInterrupt:
        stop()  # stop the robot
    except:
        stop()  # stop the robot
    finally:
        # Clean up
        mynode_.destroy_timer(timer)
        mynode_.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
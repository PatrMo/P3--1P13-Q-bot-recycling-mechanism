ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P3B' # Enter the project identifier i.e. P2A or P2B

# SERVO TABLE CONFIGURATION
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 90 # enter the value in degrees for the classification tower
drop_tube_angle = 180 # enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# BIN CONFIGURATION
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.25 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin1_metallic = False

bin2_offset = 0.25
bin2_color = [0,1,0]
bin2_metallic = False

bin3_offset = 0.25
bin3_color = [0,0,1]        
bin3_metallic = False

bin4_offset = 0.25
bin4_color = [1,1,1]        # white; changed from [0,0,0] to [1,1,1] to avoid confusing with no color
bin4_metallic = False
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
if project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
else:
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color],[bin1_metallic,bin2_metallic, bin3_metallic,bin4_metallic]]
    configuration_information = [table_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bot = qbot(0.1,ip_address,QLabs,project_identifier,hardware)
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------

import random 

#The first function we need is the dispense container function, which will, as its name suggests, allow our program to dispense one of six different bottles every time it is called
#These bottles will land on the servo table and then be picked up in the load container function. The load container function is the function that will call this function, it is
#not called in the main function.

def dispense_container():                                       #Function to dispense new containers
    num = random.randint(1, 6)                                  #Produces a random number ranging from 1-6, these numbers corrospond to one of the six bottle
    properties = table.dispense_container(num, True)            #Calls said number and assigns the properties of the new bottle to a variable
    print(properties)
    return properties                                           #Returns properties

def load_container(properties, table_vacancy):                  #Will load up to three containers onto the q-bot, will stop when certain conditions are met.
    bin_check = ''                                              #Initializing needed values for the function
    bottle_number = 0
    mass = 0
    bin = True

    while (bin == True and bottle_number < 3):                  #Checks bottle count to determine if another bottle should be loaded
        if table_vacancy == True:                               #This if statement checks if there is a bottle already on the table so another is not dropped ontop of it
            properties = dispense_container()                   #Creates a new variable in this function with the properties returned from the dispense container function
            if bottle_number == 0:                              #Checks that there is no previous bottle on table
                old_properties = properties
            new_bin = properties[2]                             #Assigns the bin number to a variable that the program can reference in the future.
        else:
            old_properties = properties                         #Properties of previous bin
            new_bin = properties[2]                             #Variable new_bin to check against old bottles bint type
            table_vacancy = True                                #Shows that table is vacant

        if old_properties[2] == new_bin:                        #Checks if the newest binID and the first binID are the same
            mass += properties[1]                               #Adds mass
            if mass >= 90:                                      #Checks total mass, if total mass is above 90 grams, will not load the next bottle
                bin = False
            else:                                               #Mass is less, and we have already checked bottle count so
                arm.move_arm(0.678, 0.0, 0.29)                  #Moves arm accordingly to place bottle
                time.sleep(2)
                arm.control_gripper(33)
                time.sleep(2)
                arm.rotate_shoulder(-4)
                time.sleep(1.5)
                arm.rotate_base(-45)
                time.sleep(1.5)
                arm.move_arm(0.278, -0.278, 0.686)
                arm.move_arm(0.0, -0.393, 0.686)
                
                if bottle_number == 0:                          #Each seperate if statement below (this one and the two beneath) simply fine tune the location of each bottle when being placed
                    bot.rotate(203)
                    time.sleep(2)
                    arm.move_arm(-0.02, -0.546, 0.537)
                    arm_deposit()
                    bot.rotate(-199)
                    
                elif bottle_number == 1:
                    time.sleep(2)
                    arm.move_arm(0.01, -0.576, 0.58)
                    arm_deposit()

                else:
                    time.sleep(2)
                    arm.move_arm(0.024, -0.48, 0.54)
                    arm_deposit()

        else:
            bin = False
        print(mass)                                             #Prints mass so the user can keep track of total
        bottle_number += 1                                      #Adds one to total number of bins to avoid going over limit
    print(bin_check)
    table_vacancy = False                                       #Sets table to no longer be vacant for next cycle
    print("transfered" , properties)                            
    return properties,old_properties, table_vacancy             #Returns table vacancy status and previous bottle properties

def arm_deposit():                                              #Repetitive code needed to drop the containers off in there location, thus made into seperate function.
    time.sleep(2)
    arm.control_gripper(-26)
    time.sleep(2)
    arm.rotate_elbow(-20)
    time.sleep(1.5)
    arm.rotate_base(40)
    arm.control_gripper(-7)
    time.sleep(1.5)
    arm.home()

def deposit_container():                                        #This function is used to bring the bot from the line to the bin, rotate the bot so that the containers can be deposited and deposit the bottle
    bot.activate_ultrasonic_sensor()
    move_distance = bot.read_ultrasonic_sensor() - 0.05         #Detect distance between bin and bot using ultrasonic sensor when depositing bottle and set a movement value to avoid bumping into bin
    bot.forward_distance(move_distance)                         
    time.sleep(1)
    bot.rotate(-100)                                           
    time.sleep(2)
    bot.activate_linear_actuator()
    bot.rotate_hopper(40)
    time.sleep(2)
    bot.deactivate_linear_actuator()
    bot.deactivate_ultrasonic_sensor()
    

def return_home():                                                                    #function to return arm back to starting position and Q-bot from bin
    arm.home()
    bot.activate_line_following_sensor()
    time.sleep(1)
    bot.rotate(-90)
    line_check = bot.line_following_sensors()
    while line_check == [0,0]:                                                        #return to line algorithm
        bot.set_wheel_speed([0.1,0.1])
        line_check = bot.line_following_sensors()
    bot.set_wheel_speed([0,0])                                                        #set q-bot straight along line
    time.sleep(1)
    bot.rotate(90)
    time.sleep(1)
    line_check = bot.line_following_sensors()     
    x,y,z = bot.position()                                                           #initializes x,y,z coordinate values
    print(x,y,z)
    bot.set_wheel_speed([0.1,0.1])
    while not ((1.52 > x and x > 1.46) and (-0.01 < y and y < 0.01)) :               #line following algorithm that checks if bot is within set range of original x,y,z values
        line_follow(line_check)
        line_check = bot.line_following_sensors()
        x,y,z = bot.position()                                                       #Setting values to check if bot still not in range yet
        print(x,y,z)
        
    bot.set_wheel_speed([0,0])
    bot.deactivate_line_following_sensor()
    bot.deactivate_ultrasonic_sensor()

def line_follow(line_check):                                                         #function for line following decision statements used in multiple other functions
    if line_check == [1,1]:
        bot.set_wheel_speed([0.1,0.1])
    elif line_check == [1,0]:
        bot.set_wheel_speed([0.06,0.1])
    elif line_check == [0,1]:
        bot.set_wheel_speed([0.1,0.06])

def transfer_container(properties):                                                 #function for transfering container from home position to appropriate bin
    transfered_properties = properties[2]
    print(transfered_properties)
    bins = ['Bin01','Bin02','Bin03','Bin04']                     #Initalizes the bins as a list that can be referenced later
    colors = [[1,0,0],[0,1,0],[0,0,1],[1,1,1]]                   #Initalizes the colours of the bins as a list (within a list) that can be refereneced later
    bot.activate_line_following_sensor()                         #Activates the line following sensor
    bot.activate_color_sensor()                                  #Activates the colour sensor
    line_check = bot.line_following_sensors()                    #Variable to store line sensor values
    
    while line_check != [0,0]:                                   #Line following and bin finiding algorithm
        color_check_optimiser = 0                                #Variable to check colour in intervals to reduce latency and prevent runtime issuess
        while color_check_optimiser < 10:                                            #loop for bot to follow track
            time.sleep(0.1)
            color_check_optimiser += 1
            line_follow(line_check)                                                  #calls line following function
            line_check = bot.line_following_sensors()
            
        bin_color = bot.read_color_sensor()[0]                                       #bin checking loop, stops at correct bin
        for i in range(4):                                                           #loop to check lists with each colour and bin type that get cycled through
            if bin_color == colors[i] and transfered_properties == bins[i]:
                line_check = [0,0]
                time.sleep(1.5)
                bot.set_wheel_speed([0,0])
                time.sleep(2)
                bot.rotate(90)

        
    bot.deactivate_color_sensor()
    bot.set_wheel_speed([0,0])
    bot.deactivate_line_following_sensor()

    
def main():                                                                           #function that runs all of the other functions
    loop = True
    table_vacancy = True                                                              #table is vacant for first iteration
    properties = ['','','']                                                           #empty properties list
    while loop == True:
        x,y,z = load_container(properties,table_vacancy)                              #set arbitrary variables to represent the oldand new properties as well as table vacancy
        properties, old_properties, table_vacancy = x,y,z                             #work around because varibales could not be initialized in previous line
        transfer_container(old_properties)
        deposit_container()
        return_home()
        
    







#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------

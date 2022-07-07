# Bot is placed at Start_1/Start_2 (0,0,0)/(3,3-5)  and moves at next node
# Bot sends the signal via Xbee module to PC about this. The orientation of the bot is known initially. (-22)/(22)
# The first traversal is from "start_coordinate" to "pebble_1_coordinate".
# The difference between "start_coordinate" and "pebble_1_coordinate" gives information about movement constraints in all directions (x,y,z) , constraints = (dx,dy,dz)
# The problem that we have to address is what direction the bot will choose in series.
# a file named 'pnemonics.txt' is also attached for clear understanding of instructions that bot will receive via xbee in form of string

'''
* Team Id : TC#975
* Author List : Rishabh, Jonas, Pawan, Kunj
* Filename: traversal.py
* Theme: Thirsty Crow
* Functions: update_bot_orientation(flag,sign), update_constraints(constraints,flag), update_bot_orientation(flag,sign), move_forward(), rotate_180_deg(), angular_turn (flag,present_orientation_of_bot), where_to_move(constraints)
* Global Variables: angular_turn_list, update_present_orientation_of_bot_list, mind_map, orientBot, direction_to_mat, counter, appended_instructions=[]
'''

import numpy as np
from path_planning import *

counter = 0
counter2 = 0;
counter3 = 0;
appended_instructions = [] # will append all traversal instruction to be send to the bot later for Complete traversal of arena

# dictionary of dictinary that outputs angular turn of the bot from node to node.
# ACW : anticlockwise, CW: clockwise
# the first key say (1,0,0) represents present bot orientation in 'x' direction
# second key represnts 'x', 'y', 'z' axis as '0', '1', '2' respectively
# the output value represnts what angle bot should move if it is facing x,yz and wants to orient in x,y or z direction
#(-1,0,0) means '-x' direction
angular_turn_list = {
   (1,0,0) : {"0" : "no turn for x",
                "1" : "ACW 60 deg turn",
                "2" : "CW 60 deg turn"},

   (0,1,0) : {"0" : "CW 60 deg turn",
                "1" : "no turn for y",
                "2" : "ACW 60 deg turn"},

    (0,0,1) : {"0" : "ACW 60 deg turn",
                 "1" : "CW 60 deg turn",
                 "2" : "no turn for z"},

    (-1,0,0) : {"0" : "no turn for -x",
                 "1" : "ACW 60 deg turn",
                 "2" : "CW 60 deg turn"},

    (0,-1,0) : {"0" : "CW 60 deg turn",
                "1" : "no turn for -y",
                "2" : "ACW 60 deg turn"},

    (0,0,-1) : {"0" : "ACW 60 deg turn",
                 "1" : "CW 60 deg turn",
                 "2" : "no turn for -z"}

}

#the first key is present orientation of the bot
#the second key is a string that represnts what angle bot desires to moves
# output is new oriention of the bot
update_present_orientation_of_bot_list ={
   (1,0,0) : {
   "No turn, move ahead" :(1,0,0),
   "ACW 120, move ahead" :(0,0,1),
   "CW 120, move ahead"  :(0,1,0)
           },  #x
   (0,1,0) : {
   "No turn, move ahead":(0,1,0),
   "ACW 120, move ahead":(1,0,0),
   "CW 120, move ahead" :(0,0,1)
          },   #y
   (0,0,1) : {
   "No turn, move ahead":(0,0,1),
   "ACW 120, move ahead":(0,1,0),
   "CW 120, move ahead" :(1,0,0)
         },   #z

   (-1,0,0) : {
   "No turn, move ahead":(-1,0,0),
   "ACW 120, move ahead":(0,0,-1),
   "CW 120, move ahead":(0,-1,0)
   },   #-x
   (0,-1,0) : {
   "No turn, move ahead":(0,-1,0),
   "ACW 120, move ahead":(-1,0,0),
   "CW 120, move ahead":(0,0,-1)
   },   #-y
   (0,0,-1) : {
   "No turn, move ahead":(0,0,-1),
   "ACW 120, move ahead":(0,-1,0),
   "CW 120, move ahead":(-1,0,0)
}   #-z

}

# mind_map is a dictionary with tuple as a Key
# key reprenst oriention of bot say (1,0,0) (meaning 'x' direction)
# the value is a list contaiting all the possible oriention that bot can takes thus describing constraints of motion
# value [0,-1,-1] means if bot faces in 'x' direction at a node then it can rotate and move in '-y' and 'z' direction only
mind_map = {
    #current_bot_direction : [x,y,z]

    (1,0,0) : [0, -1, -1],  #x
    (0,1,0): [-1, 0, -1],   #y
    (0,0,1): [-1, -1, 0],   #z

    (-1,0,0) : [0, 1, 1],   #-x
    (0,-1,0) : [1, 0, 1],   #-y
    (0,0,-1) : [1, 1, 0],   #-z

    }

#bot has reached the node , now orient it using bots direction(key 1) and orientation of marker(key 2)
# value/ output is rotation that bot has to make once it reaches the node so that is orients itself in direction of marker

orientBot = {

   (1,0,0) : {
   "33" : "No turn, move ahead",
   "11" : "ACW 120, move ahead",
   "22" : "CW 120, move ahead"
           },  #x
   (0,1,0) : {
   "22" : "No turn, move ahead",
   "33" : "ACW 120, move ahead",
   "11" : "CW 120, move ahead"
          },   #y
   (0,0,1) : {
   "11" : "No turn, move ahead",
   "22" : "ACW 120, move ahead",
   "33" : "CW 120, move ahead"
         },   #z

   (-1,0,0) : {
   "33" : "No turn, move ahead",
   "11" : "ACW 120, move ahead",
   "22" : "CW 120, move ahead"
   },   #-x
   (0,-1,0) : {
   "22" : "No turn, move ahead",
   "33" : "ACW 120, move ahead",
   "11" : "CW 120, move ahead"
   },   #-y
   (0,0,-1) : {
   "11" : "No turn, move ahead",
   "22" : "ACW 120, move ahead",
   "33" : "CW 120, move ahead"
   }   #-z
}

# dictionary that converts directions (key) to a vector matrix (list)
# it is just different represention of char into a list for easy calculations
direction_to_mat ={
     "x" : [1,0,0],
     "y" : [0,1,0],
     "z" : [0,0,1],
     "-x" : [-1,0,0],
     "-y" : [0,-1,0],
     "-z": [0,0,-1]
}

orientation_to_list = {
"11":2,
"22":1,
"33":0,

}


'''
* Function Name: update_constraints(constraints,flag)
* Input: constraints: it is a list obtained from subtracting one coordinate and final coordinate in one traversal (from pebble to pot or the other way round)
         flag : flag can assume values 0,1,2 for (+/-)(x,y,z)
* Output: returns a list of updated constraints
* Logic: whenever bot travels from one node to the other , it gets closer to the destination. since Constraints is obtained from subtracting one coordinate and final coordinate in one traversal, it is import that we update until constraints of motion becomes [0,0,0] representing bot has reached its desired destination

* Example Call: update_constraints(constraints,flag)
'''

def update_constraints(constraints,flag):


    if (constraints[flag] < 0) :
        constraints[flag] += 1


    else :
        constraints[flag] -=1

    return constraints

'''
* Function Name: update_bot_orientation(flag,sign)
* Input: sign: it is a list obtained from subtracting one coordinate and final coordinate in one traversal (from pebble to pot or the otherway round)
         flag : flag can assume values 0,1,2 for (+/-)(x,y,z)
* Output: returns a list of updated bot orientation after bot makes a angular turn
* Example Call: update_bot_orientation(flag,sign)
'''

def update_bot_orientation(flag,sign):
    temp =[0,0,0]
    temp[flag]=sign
    return temp

'''
* Function Name: move_forward()
* Input: None
* Output: appends to the list "appended_instructions" , the instruction 'w' which is pnemonics for forward motion
* Example Call: move_forward()
'''

def move_forward():
    appended_instructions.append('w')
    
'''
* Function Name: rotate_180_deg()
* Input: None
* Output: appends to the list "appended_instructions" , the instruction 's' which is pnemonics for 180 deg rotation
* Example Call: rotate_180_deg():
'''

def rotate_180_deg():
    appended_instructions.append('s')
    

'''
* Function Name: angular_turn(flag,present_orientation_of_bot)
* Input: None
* Output: appends to the list "appended_instructions" , the instruction 'a' which is pnemonics for anticlockwise 60 deg rotation
          else appends to the list "appended_instructions" , the instruction 'd' which is pnemonics for clockwise 60 deg rotation
* Logic : since we know the present orientation of bot and direction where bot must move next, we can make use of angular_turn_list which is dictionary   that will output the required rotation of bot. using this value we can append pnemonics to instruct bot later
* Example Call: rotate_180_deg():
'''

def angular_turn (flag,present_orientation_of_bot):

    turn = angular_turn_list[tuple(present_orientation_of_bot)][str(flag)]
    if turn == "ACW 60 deg turn":
        appended_instructions.append('a')
    else:
        appended_instructions.append('d')
    

'''
* Function Name: where_to_move(constraints)
* Input: constraints : a list obtained by subtracting one coordinate and final coordinate in one traversal (from pebble to pot or the other way round)
* Output: appends to the list "appended_instructions" , the instructions for full traversal of the bot that is communicated later via xbee
* Logic : since we know the present orientation of bot and direction where bot must move next, we can make use of angular_turn_list which isdictionary   that will output the required rotation of bot. using this value we can append pnemonics to instruct bot later
* Example Call: rotate_180_deg():
'''
def where_to_move(constraints) :

      global present_orientation_of_bot
      global xyz # contains freedom of movement in x,y,z direction as a list
      global appended_instructions
      global counter2
      global counter3

      #lets check if we can eliminate 120 deg rotation:
      orientation_of_aruco = orientation_to_list[all_orientations[counter2]]
      #print('lol',orientation_of_aruco)

      #we have to check if there is any chance of 180 deg rotation.
      i=0; #for indexing purpose
      counter3=abs(constraints[orientation_of_aruco])
      


      for dir_val_1 , dir_val_2 in zip(present_orientation_of_bot, constraints) :

          if(dir_val_1 * dir_val_2 < 0) :

              rotate_180_deg()
              move_forward()

              #now update the constraints
              if (constraints[i] < 0) :


                  constraints[i] += 1
                  present_orientation_of_bot = list(np.negative(present_orientation_of_bot)) #now negate the direction, realising 180_deg rotation
                  xyz = mind_map[tuple(present_orientation_of_bot)] #obtaining  freedom_of_movement

                  break

              else :

                  constraints[i] -=1
                  present_orientation_of_bot = np.negative(present_orientation_of_bot) #now negate the direction, realising 180_deg rotation
                  xyz = mind_map[tuple(present_orientation_of_bot)] #obtaining  freedom_of_movement
                  break

          i+=1

     #assuming no 180_deg rotation is required we proceed with normal algorithm

      #xyz = mind_map[ current_bot_direction] #obtaining  freedom_of_movement
      flag=0; # flag can assume values 0,1,2 for (+/-)(x,y,z)

      while(1):

          #print(flag)


          if (flag == orientation_of_aruco and counter3>=0):
              counter3=counter3-1
              flag+=1
              if(flag%3 == 0):
                  flag = 0
              

          dir_val_1 = xyz[flag] # freedom of movements given orientation of bot
          dir_val_2 = constraints[flag] # magnitude of directions that bot may take




          if(dir_val_1 * dir_val_2 > 0):

              angular_turn(flag,present_orientation_of_bot)
              move_forward()
              constraints=update_constraints(constraints,flag)
              #print(constraints,"updated constraints")
              sign = dir_val_1
              present_orientation_of_bot=update_bot_orientation(flag,sign)
              xyz = mind_map[tuple(present_orientation_of_bot)] #obtaining  freedom_of_movement
              flag+=1

              if(flag%3 == 0):
                  flag = 0


          else:

              flag+=1

              if(flag%3 == 0):
                  flag = 0


          check = all(x == 0 for x in constraints) #check for constraints becoming (0,0,0) indicating emd of one traversal
          if(check == True):
              global counter
              
              #all_orientations hold the orientations of all markers on arena.
              _is_120_turn = orientBot[tuple(present_orientation_of_bot)][all_orientations[counter]]  #check if bot needs to take 120 deg turn or not
              if _is_120_turn =="ACW 120, move ahead":
                  appended_instructions.append('A')
              elif _is_120_turn == "CW 120, move ahead":
                  appended_instructions.append('D')



              
              #even counter implies that bot has reached pebble marker and we need to do the following tasks
              # 1. energise the magnet                       : 'P'
              # 2. move a bit ahead (magnet is picked now)   : 'W'
              # 3. change the corresponding AR pebble diminished : 'J'
              # 4. move straight back a bit to the node      : 'S'
              if counter%2 == 0:
                  appended_instructions.append('P') # energise the magnet
                  appended_instructions.append('W') # move a bit ahead (magnet is picked now)
                  appended_instructions.append('J') # communicate to pc do that  AR of pebble can be changed
                  
                  appended_instructions.append('S') # move a bit backward
                  
                  #the next task is to update "present_orientation_of_bot" since bot has changed its direction
                  present_orientation_of_bot=list(update_present_orientation_of_bot_list[tuple(present_orientation_of_bot)][orientBot[tuple(present_orientation_of_bot)][all_orientations[counter]]])

                  xyz = mind_map[tuple(present_orientation_of_bot)] #obtaining  freedom_of_movement

                  #odd counter implies that bot has reached water marker and we need to do the following tasks
                  # 1. move a bit ahead (magnet is picked now)   : 'W'
                  # 2. denergise the magnet                       : 'T'
                  # 3. change the corresponding AR water level up : 'K'
                  # 4. move straight back a bit to the node      : 'S'

              else:

                  appended_instructions.append('W') # move a bit ahead (magnet is picked now)
                  
                  appended_instructions.append('T') # denergise the magnet
                  
                  appended_instructions.append('K') #communicate to pc do that  AR of pot can be changed
                  appended_instructions.append('S') # move a bit backward
                  
                  #the next task is to update "present_orientation_of_bot" since bot has changed its direction
                  present_orientation_of_bot=list(update_present_orientation_of_bot_list[tuple(present_orientation_of_bot)][orientBot[tuple(present_orientation_of_bot)][all_orientations[counter]]])

                  xyz = mind_map[tuple(present_orientation_of_bot)] #obtaining  freedom_of_movement


              counter+=1
              counter3=0
              counter2=counter2+1

              #print(present_orientation_of_bot)
              break



current_bot_direction =  start_orientation
present_orientation_of_bot = direction_to_mat[current_bot_direction]  #[0,0,-1]
xyz = mind_map[tuple(present_orientation_of_bot)] #obtaining  freedom_of_movement




for i in range(6):
    print("moving from "+str(all_cords[i])+" to "+str(all_cords[i+1])+" :")
    Constraints = list(np.subtract(all_cords[i+1], all_cords[i]))
    print(" ")
    print(" -------------------------------------")
    print(" ")
    where_to_move(Constraints)


appended_instructions.append('z') # buzzer on to signal end of traversal
appended_instructions.append('Z') # buzzer off
appended_instructions.append('.') # end


#appended_instructions is used in GLteapot.py for sending instructions to bot via xbee and also AR projection

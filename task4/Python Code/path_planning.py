'''
* Team Id : TC#975
* Author List : Rishabh, Jonas, Pawan, Kunj
* Filename: path_planning.py
* Theme: Thirsty Crow
* Functions: find_coordinates(arena_config,Robot_start),key_for_arena_config()
* Global Variables: start_coordinate=[], start_orientation="", water_coordinate_1=[], water_coordinate_2=[], pebble_1_coordinate_1=[], pebble_1_coordinate_2=[], pebble_2_coordinate_1=[], pebble_2_coordinate_2=[], pebble_3_coordinate_1=[], pebble_3_coordinate_2=[], pebble_1_coordinate=[], pebble_2_coordinate=[], pebble_3_coordinate=[], water_from_p1=[], water_from_p2=[], water_from_p3=[], p1_orientation=[], p2_orientation=[], p3_orientation=[], water_orientation =[], all_cords = [], all_orientations=[]
'''

import numpy as np

start_coordinate=[]  #holds co-ordinate of start position ,say [0,0,0] for Start-1
start_orientation=""  # holds the orientation of corresponding start_coordinate , say [0,0,-1] representing -z axis

water_coordinate_1=[] # first coordinate of water/pot marker
water_coordinate_2=[] # second coordinate of water/pot marker
pebble_1_coordinate_1=[] #first coordinate of first pebble
pebble_1_coordinate_2=[] #second coordinate of first pebble
pebble_2_coordinate_1=[] #first coordinate of second pebble
pebble_2_coordinate_2=[] #second coordinate of second pebble
pebble_3_coordinate_1=[] #first coordinate of third pebble
pebble_3_coordinate_2=[] #second coordinate of third pebble

pebble_1_coordinate=[]   # final coordinate of first pebble ( which is traversed in less time)
pebble_2_coordinate=[]   #  final coordinate of second pebble
pebble_3_coordinate=[]   # final coordinate of third pebble

water_from_p1=[] #final coordinate of pot from first pebble ( which is traversed in less time)
water_from_p2=[] #final coordinate of pot second pebble ( which is traversed in less time)
water_from_p3=[] #final coordinate of pot third pebble ( which is traversed in less time)

p1_orientation=[] #oriention of first pebble , say [11]
p2_orientation=[] #oriention of second pebble , say [22]
p3_orientation=[] #oriention of third pebble , say [11]
water_orientation =[] #oriention of pot/water , say [33]
indeX=[] # to obatin keys for arena-config



all_cords = []    #it is a list of updated values of all coordinates including "start_coordinate,pebble_1_coordinate, water_from_p1, pebble_2_coordinate, water_from_p2, pebble_3_coordinate, water_from_p3"
all_orientations=[] # it is a list of updated values of all orientations including "p1_orientation,water_orientation,p2_orientation,water_orientation,p3_orientation,water_orientation"


# cells contating pebble which are nearer to  start position are given higher preference
priority_cell_from_start1={10:1,
                           5:2,
                           15:3,
                           6:4,
                           11:5,
                           2:6,
                           16:7,
                           7:8,
                           12:9,
                           1:10,
                           17:11,
                           8:12,
                           13:13,
                           4:14,
                           5:15,
                           18:16,
                           14:17,
                           9:18,
                           19:19
                           }

priority_cell_from_start2={14:1,19:2,9:3,13:4,8:5,18:6,4:7,7:8,12:9,3:10,17:11,1:12,11:13,6:14,16:15,2:16,10:17,15:18,5:19}

'''
* Function Name: key_for_arena_config()
* Input: None
* Output: returns None , just updates the required global variables (indeX)
* Logic: all cells are ranked from start position. we will form a indeX list(the values are keys of aruco_list)
   that will contain the pebbles pick up in order of shortest path according to rank.
* Example Call: key_for_arena_config()
'''

def key_for_arena_config():
    if Robot_start == "START-1" :

        


        keys=arena_config.keys() # obtain all keys from arena_config
        cell_available=[]
        rank=[]
        sort_cell = []
        lol={}
        for key in keys:
            cell_available.append(arena_config[key][1])
        

        cell_available=cell_available[1:]
        key_list = list(keys)[1:]
        

        for key in keys:
        
            lol[arena_config[key][1]]=key
    
           

        for cell in cell_available:
             
             rank.append(priority_cell_from_start1[cell])
       
    
        rank.sort() #obtain rank in sorted order
        
    

        for r in rank:
            for cell in cell_available:
                    if r == priority_cell_from_start1[cell]:
                        sort_cell.append(cell)

               
            
        for cell in range(3):
            indeX.append(lol[sort_cell[cell]]) # indeX will contain key for aruco marker that is nearset to access by bot in ascending order

        

    else:

        keys=arena_config.keys()
        cell_available=[]
        rank=[]
        sort_cell = []
        lol={}
        for key in keys:
            cell_available.append(arena_config[key][1])
        

        cell_available=cell_available[1:]
        key_list = list(keys)[1:]
        

        for key in keys:
        
            lol[arena_config[key][1]]=key
    
           

        for cell in cell_available:
             
             rank.append(priority_cell_from_start2[cell])
       
    
        rank.sort()  #obtain rank in sorted order
        
    

        for r in rank:
            for cell in cell_available:
                    if r == priority_cell_from_start2[cell]:
                        sort_cell.append(cell)

                   
            
        for cell in range(3):
            indeX.append(lol[sort_cell[cell]])  # indeX will contain key for aruco marker that is nearset to access by bot in ascending order

        

   
# graphing the arena
# arena_graph is a dictionary that holds two co-ordinates 'left' and 'right' namely 'L' and 'R' given cell number and orientation.
arena_graph = {
    "1 33" : {"L" : [3,0,-2],
              "R" : [4,-1,-3]},
    "2 33" : {"L" : [2,0,-1],
              "R" : [3,-1,-2]},
    "3 33" : {"L" : [2,1,-2],
              "R" : [3,0,-3]} ,
    "4 33" : {"L" : [3,1,-3],
              "R" : [4,0,-4]},
    "5 33" : {"L" : [1,0,0],
              "R" : [2,-1,-1]},
    "6 33" : {"L" : [1,1,-1],
              "R" : [2,0,-2]},
    "7 33" : {"L" : [1,2,-2],
              "R" : [2,1,-3]},
    "8 33" : {"L" : [2,2,-3],
              "R" : [3,1,-4]},
    "9 33" : {"L" : [3,2,-4],
              "R" : [4,1,-5]},
    "10 33": {"L" : [0,1,0],
              "R" : [1,0,-1]},
    "11 33": {"L" : [0,2,-1],
              "R" : [1,1,-2]},
    "12 33": {"L" : [0,3,-2],
              "R" : [1,2,-3]},
    "13 33": {"L" : [1,3,-3],
              "R" : [2,2,-4]},
    "14 33": {"L" : [2,3,-4],
              "R" : [3,2,-5]},
    "15 33": {"L" : [-1,2,0],
              "R" : [0,1,-1]},
    "16 33": {"L" : [-1,3,-1],
              "R" : [0,2,-2]},
    "17 33": {"L" : [-1,4,-2],
              "R" : [0,3,-3]},
    "18 33": {"L" : [0,4,-3],
              "R" : [1,3,-4]},
    "19 33": {"L" : [1,4,-4],
              "R" : [2,3,-5]},




    "1 11" : {"L" : [3,-1,-2],
              "R" : [4,0,-3]},
    "2 11" : {"L" : [2,-1,-1],
              "R" : [3,0,-2]},
    "3 11" : {"L" : [2,0,-2],
              "R" : [3,1,-3]},
    "4 11" : {"L" : [3,0,-3],
              "R" : [4,1,-4]},
    "5 11" : {"L" : [1,-1,0],
              "R" : [2,0,-1]},
    "6 11" : {"L" : [1,0,-1],
              "R" : [2,1,-2]},
    "7 11" : {"L" : [1,-1,0],
              "R" : [2,0,-1]},
    "8 11" : {"L" : [2,1,-3],
              "R" : [3,2,-4]},
    "9 11" : {"L" : [3,1,-4],
              "R" : [4,2,-5]},
    "10 11": {"L" : [0,0,0],
              "R" : [1,1,-1]},
    "11 11": {"L" : [0,1,-1],
              "R" : [1,2,-2]},
    "12 11": {"L" : [0,2,-2],
              "R" : [1,3,-3]},
    "13 11": {"L" : [1,2,-3],
              "R" : [2,3,-4]},
    "14 11": {"L" : [2,2,-4],
              "R" : [3,3,-5]},
    "15 11": {"L" : [-1,1,0],
              "R" : [0,2,-1]},
    "16 11": {"L" : [-1,2,-1],
              "R" : [0,3,-2]},
    "17 11": {"L" : [-1,3,-2],
              "R" : [0,4,-3]},
    "18 11": {"L" : [0,3,-3],
              "R" : [1,4,-4]},
    "19 11": {"L" : [1,3,-4],
              "R" : [2,4,-5]},


    "1 22" : {"L" : [4,-1,-2],
              "R" : [3,0,-3]},
    "2 22" : {"L" : [3,-1,-1],
              "R" : [2,0,-2]},
    "3 22" : {"L" : [3,0,-2],
              "R" : [2,1,-3]},
    "4 22" : {"L" : [4,0,-3],
              "R" : [3,1,-4]},
    "5 22" : {"L" : [2,-1,0],
              "R" : [1,0,-1]},
    "6 22" : {"L" : [2,0,-1],
              "R" : [1,1,-2]},
    "7 22" : {"L" : [2,1,-2],
              "R" : [1,2,-3]},
    "8 22" : {"L" : [3,1,-3],
              "R" : [2,2,-4]},
    "9 22" : {"L" : [4,1,-4],
              "R" : [3,2,-5]},
    "10 22": {"L" : [1,0,0],
              "R" : [0,1,-1]},
    "11 22": {"L" : [1,1,-1],
              "R" : [0,2,-2]},
    "12 22": {"L" : [1,2,-2],
              "R" : [0,3,-3]},
    "13 22": {"L" : [2,2,-3],
              "R" : [1,3,-4]},
    "14 22": {"L" : [3,2,-4],
              "R" : [2,3,-5]},
    "15 22": {"L" : [0,1,0],
              "R" : [-1,2,-1]},
    "16 22": {"L" : [0,2,-1],
              "R" : [-1,3,-2]},
    "17 22": {"L" : [0,3,-2],
              "R" : [-1,4,-3]},
    "18 22": {"L" : [1,3,-3],
              "R" : [0,4,-4]},
    "19 22": {"L" : [2,3,-4],
              "R" : [1,4,-5]},
}

'''
* Function Name: find_coordinates(arena_config,Robot_start)
* Input: arena_config : A python dictionary that holds arena arena_configration
         Robot_start : Starting position of robot ( namely, Start_1 or Start_2)
* Output: returns None , just updates the required global variables
* Logic: The value of dictionary is a string. Extracting and separating the strings and then using it as a Key for 'arena_graph'
         Thus obtaining co-ordinate for each markers.

* Example Call: find_coordinates(arena_config,Robot_start)
'''


def find_coordinates(arena_config,Robot_start):

    # Two water marker coordinates
    water=(str(arena_config[0][1])+' '+arena_config[0][2]).replace('-','')
    global water_coordinate_1
    water_coordinate_1 = arena_graph[water]["L"]
    global water_coordinate_2
    water_coordinate_2 = arena_graph[water]["R"]
    global water_orientation
    water_orientation = (arena_config[0][2]).replace('-','')
    


    # Two pebble_1 marker coordinates
    
    pebble_1=((str(arena_config[indeX[0]][1])+' '+arena_config[indeX[0]][2]).replace('-','')) #3 11
    global pebble_1_coordinate_1
    pebble_1_coordinate_1 = arena_graph[pebble_1]["L"]
    
    global pebble_1_coordinate_2
    pebble_1_coordinate_2 = arena_graph[pebble_1]["R"]
    global p1_orientation
    p1_orientation = (arena_config[indeX[0]][2]).replace('-','')
    


    # Two pebble_2 marker coordinates

    pebble_2=((str(arena_config[indeX[1]][1])+' '+arena_config[indeX[1]][2]).replace('-','')) #11 33
    global pebble_2_coordinate_1
    pebble_2_coordinate_1 = arena_graph[pebble_2]["L"]
    global pebble_2_coordinate_2
    pebble_2_coordinate_2 = arena_graph[pebble_2]["R"]
    global p2_orientation
    p2_orientation = (arena_config[indeX[1]][2]).replace('-','')

    # Two pebble_3 marker coordinates

    pebble_3=((str(arena_config[indeX[2]][1])+' '+arena_config[indeX[2]][2]).replace('-','')) #13 22
    global pebble_3_coordinate_1
    pebble_3_coordinate_1 = arena_graph[pebble_3]["L"]
    global pebble_3_coordinate_2
    pebble_3_coordinate_2 = arena_graph[pebble_3]["R"]
    global p3_orientation
    p3_orientation = (arena_config[indeX[2]][2]).replace('-','')

    # obtaining start coordinate
    global start_coordinate
    global start_orientation
    if Robot_start == "START-1" :

        start_coordinate = [0,0,0]
        start_orientation = "-z"
    else :

        start_coordinate = [3,3,-5]
        start_orientation = "z"



#It is provided as a input dictionaryself.
arena_config = {0: ("Water Pitcher", 7, "3-3"), 1:("Pebble",1, "2-2"), 3:("Pebble", 14, "1-1"), 5:("Pebble", 15, "3-3")}
Robot_start = "START-2"


#main function begins

def main():
  # must be called for co0rdinate extraction and updating global variables
  find_coordinates(arena_config,Robot_start)

  '''
  for every orientation there are two positions from where bot can access the respective marker. Finding the co-ordinate that gives shortest distance by using distance formula
  '''

  # finding shortest distance between start and first pebble (pebble_1)
  global pebble_1_coordinate
  if sum(np.absolute(np.subtract(pebble_1_coordinate_1,start_coordinate))) <=  sum(np.absolute(np.subtract(pebble_1_coordinate_2,start_coordinate))):
      pebble_1_coordinate = pebble_1_coordinate_1
  else :
      pebble_1_coordinate = pebble_1_coordinate_2

  #finding shortest distance between first pebble (pebble_1) and water marker
  global water_from_p1
  if sum(np.absolute(np.subtract(water_coordinate_1,pebble_1_coordinate))) <=  sum(np.absolute(np.subtract(water_coordinate_2,pebble_1_coordinate))):
      water_from_p1 = water_coordinate_1
  else:
      water_from_p1 = water_coordinate_2

  #finding shortest distance between water marker and second pebble (pebble_2)
  global pebble_2_coordinate
  if sum(np.absolute(np.subtract(pebble_2_coordinate_1,water_from_p1))) <=  sum(np.absolute(np.subtract(pebble_2_coordinate_2,water_from_p1))):

      pebble_2_coordinate = pebble_2_coordinate_1
  else :
      pebble_2_coordinate = pebble_2_coordinate_2

  #finding shortest distance between first pebble (pebble_1) and water marker
  global water_from_p2
  if sum(np.absolute(np.subtract(water_coordinate_1,pebble_2_coordinate))) <=  sum(np.absolute(np.subtract(water_coordinate_2,pebble_2_coordinate))):
      water_from_p2 = water_coordinate_1
  else:
      water_from_p2 = water_coordinate_2

  #finding shortest distance between water marker and second pebble (pebble_2)
  global pebble_3_coordinate
  if sum(np.absolute(np.subtract(pebble_3_coordinate_1,water_from_p2))) <=  sum(np.absolute(np.subtract(pebble_3_coordinate_2,water_from_p2))):
      pebble_3_coordinate = pebble_3_coordinate_1
  else :
      pebble_3_coordinate = pebble_3_coordinate_2

   #finding shortest distance between first pebble (pebble_3) and water marker
  global water_from_p3
  if sum(np.absolute(np.subtract(water_coordinate_1,pebble_3_coordinate))) <=  sum(np.absolute(np.subtract(water_coordinate_2,pebble_3_coordinate))):
      water_from_p3 = water_coordinate_1
  else:
      water_from_p3 = water_coordinate_2

  '''
  putting all the obtained values in a list for easier access and manipulation glTexParameterf
  '''
  global all_cords
  all_cords = [start_coordinate,pebble_1_coordinate, water_from_p1, pebble_2_coordinate, water_from_p2, pebble_3_coordinate, water_from_p3]
  global all_orientations
  all_orientations = [p1_orientation,water_orientation,p2_orientation,water_orientation,p3_orientation,water_orientation]

key_for_arena_config()
main()

if __name__=="__main__":


   
    #printing for DEBUGGING:
    print("all coordiantes obtained")

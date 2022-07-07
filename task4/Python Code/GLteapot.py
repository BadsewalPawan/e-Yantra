'''
* Team Id : TC#975
* Author List :  Pawan, Rishabh, Jonas, Kunj
* Filename: GLteapot.py
* Theme: Thirsty Crow
* Functions: communicate_instruction(), getCameraMatrix(), get_bot_data(),init_gl(), resize(),drawGLScene(),detect_markers(),draw_background(), init_object_texture()
* Global Variables:texture_object,texture_background,dist_coeff, cap,crow,pebble_dim,pebble_initial,pot_initial,pot_low ,pot_mid ,pot_high ,flag_pebble_1,flag_pebble_2,flag_pebble_3,flag_pot,index
'''


import numpy as np
import cv2
import cv2.aruco as aruco
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import pygame
import time
import serial
from objloader import *
from traversal import appended_instructions #this list will be used to communicate instructions to bot for the traversal


texture_object = None
texture_background = None
camera_matrix = None
dist_coeff = None
cap = cv2.VideoCapture(1)

crow = None     #will hold the object definition of crow.obj

pebble_initial = None #will hold the object definition of pebble_initial.obj
pebble_dim = None
pebble1_dim =None
pebble2_dim =None

pot_initial = None
pot_low = None
pot_mid = None
pot_high = None  #will hold the object definition of pot_high.obj

flag_pebble_1=0 #flags determine the AR state of pebble_1 etc
flag_pebble_2=0
flag_pebble_3=0
flag_pot=0
index=0          # for counter purpose

ser = serial.Serial("COM3", 9600, timeout=0.05) #establishing serial communication


INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [ 1.0, 1.0, 1.0, 1.0]])

################## Define Utility Functions Here #######################
"""
Function Name : getCameraMatrix()
Input: None
Output: camera_matrix, dist_coeff
Purpose: Loads the camera calibration file provided and returns the camera and
         distortion matrix saved in the calibration file.
"""
def getCameraMatrix():
        global camera_matrix, dist_coeff
        with np.load('System.npz') as X:
                camera_matrix, dist_coeff, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]

"""
Function Name : communicate_instruction()
Input: None
Output: None
Purpose: transfers all the appended_instructions one by one at once to the bot in form of character
"""

def communicate_instruction():

    global appended_instructions
    #ser = serial.Serial("COM3", 9600, timeout=0.05)

    for i in appended_instructions:
            ser.write(str.encode(i))   #send all instructions  to bot via  xbee

            received_char=ser.read().decode('utf8')
            



"""
Function Name : get_bot_data()
Input: None
Output: None
Purpose: receives instructions from  the bot in form of character to change AR of pot and pebble
"""

def get_bot_data():

                global index   #for counting number of times this function is called
                               #an 'even' count of index means call for change in AR pot
                global flag_pot
                global flag_pebble_1
                global flag_pebble_2
                global flag_pebble_3
                global lol

                data=ser.read()
                #data = unicode(data, errors='ignore') progress task wala
                data=data.decode('unicode_escape')
                print(data)

                #check is data=='J' or 'K' indicating change of pebble AR or pot AR respectively
                if data == 'J':
                     if index == 0:
                         flag_pebble_1 +=1
                         index=index+1
                     elif index == 2:
                         flag_pebble_2 +=1
                         index=index+1
                     elif index == 4:
                        flag_pebble_3 +=1
                        index=index+1

                if data == 'K':

                    if index %2 != 0:
                        flag_pot += 1
                        index=index+1
                        print(index)

                ser.write(str.encode('c'))







########################################################################

############# Main Function and Initialisations ########################
"""
Function Name : main()
Input: None
Output: None
Purpose: Initialises OpenGL window and callback functions. Then starts the event
         processing loop.
"""
def main():
        glutInit()
        getCameraMatrix()
        communicate_instruction()  # this will send a string of instructions to bot for the traversal at tge start of program

        glutInitWindowSize(640, 480)
        glutInitWindowPosition(0,0)
        glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
        window_id = glutCreateWindow("OpenGL")
        init_gl()
        glutDisplayFunc(drawGLScene)
        glutIdleFunc(drawGLScene)
        glutReshapeFunc(resize)
        glutMainLoop()
        #nothing works down from here in this main function



"""
Function Name : init_gl()
Input: None
Output: None
Purpose: Initialises various parameters related to OpenGL scene.
"""
def init_gl():
        global texture_object, texture_background
        global crow
        global pebble_initial
        global pebble_dim
        global pot_initial
        global pot_low
        global pot_mid
        global pot_high
        global pebble1_dim
        global pebble2_dim 
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        texture_background = glGenTextures(1)
        texture_object = glGenTextures(1)
        crow = OBJ('crow.obj', swapyz=True)
        pebble_initial = OBJ('pebble_initial.obj', swapyz=True)
        pebble_dim = OBJ('pebble_dim.obj', swapyz=True)
        pot_initial=OBJ('pot_initial.obj', swapyz=True)
        pot_low=OBJ('pot_low.obj', swapyz=True)
        pot_mid=OBJ('pot_mid.obj', swapyz=True)
        pot_high=OBJ('pot_high.obj', swapyz=True)

"""
Function Name : resize()
Input: None
Output: None
Purpose: Initialises the projection matrix of OpenGL scene
"""
def resize(w,h):
        ratio = 1.0* w / h
        glMatrixMode(GL_PROJECTION)
        glViewport(0,0,w,h)
        gluPerspective(81.6, ratio, 0.1, 200.0) 

"""
Function Name : drawGLScene()
Input: None
Output: None
Purpose: It is the main callback function which is called again and
         again by the event processing loop. In this loop, the webcam frame
         is received and set as background for OpenGL scene. ArUco marker is
         detected in the webcam frame and 3D model is overlayed on the marker
         by calling the overlay() function.
"""
def drawGLScene():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ar_list = []
        ret, frame = cap.read()

        #reading value from buffer (if any) and performing respective AR changes
        get_bot_data()





        if ret == True:
                draw_background(frame)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                ar_list = detect_markers(frame)



                for i in ar_list:
                        

                        if i[0] == 10:
                                
                                overlay(frame, ar_list, i[0],"crow")
                                

                        if i[0] == 0:
                                
                                overlay(frame, ar_list, i[0],"water_pitcher")

                        if i[0] == 3:
                                
                                overlay(frame, ar_list, i[0],"pebble_1")
                                
                        if i[0] == 1:
                                
                                overlay(frame, ar_list, i[0],"pebble_2")

                        if i[0] == 5:
                                
                                overlay(frame, ar_list, i[0],"pebble_3")
                                


                #frame=cv2.flip(frame,1)
                cv2.imshow('frame', frame)
                cv2.waitKey(1)
        glutSwapBuffers()

########################################################################

######################## Aruco Detection Function ######################
"""
Function Name : detect_markers()
Input: img (numpy array)
Output: aruco list in the form [(aruco_id_1, centre_1, rvec_1, tvec_1),(aruco_id_2,
        centre_2, rvec_2, tvec_2), ()....]
Purpose: This function takes the image in form of a numpy array, camera_matrix and
         distortion matrix as input and detects ArUco markers in the image. For each
         ArUco marker detected in image, paramters such as ID, centre coord, rvec
         and tvec are calculated and stored in a list in a prescribed format. The list
         is returned as output for the function
"""
def detect_markers(img):


        ################################################################
        #################### Same code as Task 1.1 #####################
        ################################################################
        markerLength = 100
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        aruco_list = []
        aruco_list_in=[]
        ######################## INSERT CODE HERE ########################
        idd=[]

        centre=[]

        aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)

        parameters = aruco.DetectorParameters_create()

        corners, ids, _ = aruco.detectMarkers(gray, aruco_dict,parameters = parameters)
        rvec, tvec ,_= aruco.estimatePoseSingleMarkers(corners, markerLength, camera_matrix, dist_coeff)
        aruco.drawDetectedMarkers(img,corners, ids)

        if ids is None :
                pass

        else:
                idd=ids.ravel()  # works only when ids is not empty

        i=0


        centre=[]

        for q in corners:
        
            m1 = (q[0][1][1] -q[0][3][1])/(q[0][1][0] - q[0][3][0]);
            m2 = (q[0][0][1] - q[0][2][1])/(q[0][0][0] - q[0][2][0]);
            x = ((m1*q[0][3][0] - m2*q[0][2][0] + q[0][2][1] - q[0][3][1])/(m1 - m2));
            y = (m1*(x - q[0][3][0]) + q[0][3][1]);
            centre.append((x,y))





        for d in idd:
            aruco_list_in.append(d)
            aruco_list_in.append(centre[i])
            aruco_list_in.append(rvec[i].reshape(1,1,3))

            aruco_list_in.append(tvec[i].reshape(1,1,3))
            aruco_list.append(tuple(aruco_list_in))
            aruco_list_in=[]
            i+=1

        
        return aruco_list
########################################################################


################# This is where the magic happens !! ###################
############### Complete these functions as  directed ##################
"""
Function Name : draw_background()
Input: img (numpy array)
Output: None
Purpose: Takes image as input and converts it into an OpenGL texture. That
         OpenGL texture is then set as background of the OpenGL scene
"""
def draw_background(img):

  bg_image=cv2.flip(img,0)

  bg_image=Image.fromarray(bg_image)

  width=bg_image.size[0]
  height=bg_image.size[1]


  bg_image=bg_image.tobytes("raw","BGRX",0,-1)

  glEnable(GL_TEXTURE_2D)

  glBindTexture(GL_TEXTURE_2D,texture_background)


  #this one is necessary with texture2d for some reason
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
  glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_image)

  
  glBindTexture(GL_TEXTURE_2D,texture_background)
  glPushMatrix()
  glTranslate(0.0,0.0,0.0)

  # Draw textured Quads

  glBegin(GL_QUADS)
  glTexCoord2f(0.0, 0.0)
  glVertex3f(-1.0, 1.0, -1.0)
  glTexCoord2f(1.0, 0.0)
  glVertex3f(1.0, 1.0, -1.0)
  glTexCoord2f(1.0, 1.0)
  glVertex3f(1.0, -1.0, -1.0)
  glTexCoord2f(0.0, 1.0)
  glVertex3f(-1.0, -1.0, -1.0)
  glEnd()
  glPopMatrix()


  return None

"""
Function Name : init_object_texture()
Input: Image file path
Output: None
Purpose: Takes the filepath of a texture file as input and converts it into OpenGL
         texture. The texture is then applied to the next object rendered in the OpenGL
         scene.
"""
def init_object_texture(image_filepath):


        tex = cv2.imread(image_filepath)
        tex=cv2.flip(tex,0)
        tex=Image.fromarray(tex)
        width=tex.size[0]
        height=tex.size[1]
        tex=tex.tobytes("raw","BGRX",0,-1)
        glEnable(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D,texture_object)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        return None

"""
Function Name : overlay()
Input: img (numpy array), aruco_list, aruco_id, texture_file (filepath of texture file)
Output: None
Purpose: Receives the ArUco information as input and overlays the 3D Model of a teapot
         on the ArUco marker. That ArUco information is used to
         calculate the rotation matrix and subsequently the view matrix. Then that view matrix
         is loaded as current matrix and the 3D model is rendered.

         Parts of this code are already completed, you just need to fill in the blanks. You may
         however add your own code in this function.
"""

def overlay(img, ar_list, ar_id, obj_file):
        for x in ar_list:
                if ar_id == x[0]:
                        _, rvec, tvec = x[1], x[2], x[3]
        rmtx = cv2.Rodrigues(rvec)[0]
        


        ######################## INSERT CODE HERE ########################

        pts = np.float32([[0,0,0]]) #2d points on centre of marker in camera world


        pt_dict = {}
        imgpts, _ = cv2.projectPoints(pts, rvec, tvec, camera_matrix, dist_coeff)
        for i in range(len(pts)):
                 pt_dict[tuple(pts[i])] = tuple(imgpts[i].ravel())
        src = pt_dict[tuple(pts[0])]

        og_centre=src  #centre of marker in pixel value in captured frame


        #opengl window is normalized from -0.5 to 0.5 in both axis (x,y)
        # thus translating and scaling (change of axis) to correctly overlay the AR object
        a=1/640.00
        b=1/480.0
        X=og_centre[0]
        Y=og_centre[1]

        x=(X-320)*a
        y=(Y-240)*b
        z=tvec[0][0][2]/5000;

        # if z is less than 1 then  size increases . At z=1 half portion of teapot vanishes..do z=1 is not safe
        #                                            AT z=0.1 object is very big. we r partially inside object


        view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],x],
                        [rmtx[1][0],rmtx[1][1],rmtx[1][2],y],
                        [rmtx[2][0],rmtx[2][1],rmtx[2][2],z],
                        [0.0       ,0.0       ,0.0       ,1.0    ]])



        view_matrix = view_matrix * INVERSE_MATRIX
        view_matrix = np.transpose(view_matrix)


        glPushMatrix()

        glLoadMatrixd(view_matrix)


        if obj_file == "crow" :
                
                glCallList(crow.gl_list)


        if obj_file =="water_pitcher":
            if flag_pot == 0:
                
                glCallList(pot_initial.gl_list)
            elif flag_pot == 1:
                
                glCallList(pot_low.gl_list)
            elif flag_pot == 2:
                
                glCallList(pot_mid.gl_list)
            elif flag_pot == 3:
                glCallList(pot_high.gl_list)
                


        if obj_file == "pebble_1":
            if flag_pebble_1 == 0:
                
                glCallList(pebble_initial.gl_list)
            elif flag_pebble_1 == 1:
                
                glCallList(pebble_dim.gl_list)


        elif obj_file =="pebble_2":
            if flag_pebble_2 == 0:
                
                glCallList(pebble_initial.gl_list)
            elif flag_pebble_2 == 1:
                
                glCallList(pebble_dim.gl_list)

        elif obj_file =="pebble_3":
            if flag_pebble_3 == 0:
                glCallList(pebble_initial.gl_list)
            elif flag_pebble_3 == 1:
                glCallList(pebble_dim.gl_list)


        glPopMatrix()



########################################################################

if __name__ == "__main__":
        main()

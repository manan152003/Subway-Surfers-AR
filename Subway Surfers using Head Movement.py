import cv2 as cv
import mediapipe as mp
from time import time
from math import hypot
import pyautogui 


mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

# FPS
pTime = 0
def calculate_fps(img):
    global pTime
    cTime = time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv.putText(img, str(int(fps)), (10,70), cv.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
    return img


# Detect Pose
def detect_pose(img, draw=True):
    imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    
    # Draw landmarks and connections
    if results.pose_landmarks :
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS) 

    return results

# Checking left and right 

def check_left_right(img, results):

    horizontal_position = None

    height, width, _ = img.shape

    nose_corr = int(results.pose_landmarks.landmark[mpPose.PoseLandmark.NOSE].x * width)

    if(nose_corr < (width//2)-175):

        horizontal_position = "Left"
    elif(nose_corr > (width//2)+175):

        horizontal_position = "Right"
    elif(nose_corr >= (width//2)-175 and nose_corr <= (width//2)+175):

        horizontal_position = "Center"

    return horizontal_position

# Up and Down Movements

def check_up_down(img, results, NOSS_CORR = 250):
    
        vertical_position = None
    
        height, width, _ = img.shape
    
        nose_corr = int(results.pose_landmarks.landmark[mpPose.PoseLandmark.NOSE].y * height)

        lower_bound = NOSS_CORR-125
        upper_bound = NOSS_CORR+50
    
        if(nose_corr < lower_bound):

            vertical_position = "Jumping"
        elif(nose_corr > upper_bound): 

            vertical_position = "Rolling"
        else:

            vertical_position = "Standning"
    
        return vertical_position

#  Checking nose in circle or not

def check_circle(img, results):
        
            circle_position = None
        
            height, width, _ = img.shape
        
            nose_corr_x = int(results.pose_landmarks.landmark[mpPose.PoseLandmark.NOSE].x * width)
            nose_corr_y = int(results.pose_landmarks.landmark[mpPose.PoseLandmark.NOSE].y * height)
        
            center_x = width//2
            center_y = height//2
        
            distance = hypot(nose_corr_x - center_x, nose_corr_y - center_y)
        
            if(distance < 100):
                circle_position = "Inside"
            else:
                circle_position = "Outside"
        
            return circle_position

# Initializing the video capture
cam = cv.VideoCapture(0)
cam.set(3, 1280)
cam.set(4, 720)

cv.namedWindow('Subway Surfers using Head Movement', cv.WINDOW_NORMAL)

# Initialling the vairaibles

game_started = False

lane_index = 1   #center=1, left=0, right=2

jump_index = 1   #center=1, roll=0, jump=2

NOS_CORR = None

counter = 0

num_of_frames = 30

# Starting the cam
while cam.isOpened():

    ok, img = cam.read()
    if not ok:
        continue


    img = cv.flip(img, 1)

    img_height, img_width, _ = img.shape

    # Pose detection
    results = detect_pose(img)

    # Checking if the pose landmarks are detected
    if results.pose_landmarks:
    
        if game_started:

            #  HORIZONTAL MOVEMENTS 
            # ----------------------
            cv.line(img, ((img_width//2)-175, 0), ((img_width//2)-175, img_height), (255,255,255), 3)
            cv.line(img, ((img_width//2)+175, 0), ((img_width//2)+175, img_height), (255,255,255), 3)
            cv.line(img, ((0, img_height//2+50)), ((img_width, img_height//2+50)), (255,255,255), 3)
            cv.line(img, ((0, img_height//2-125)), ((img_width, img_height//2-125)), (255,255,255), 3)


            horizontal_position = check_left_right(img, results)

            if (horizontal_position == "Left" and lane_index != 0) or (horizontal_position == "Center" and lane_index == 2):
                pyautogui.press('left')
                cv.putText(img, "Left", (5,img_height-10), cv.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
                lane_index -= 1

            elif (horizontal_position == "Right" and lane_index != 2) or (horizontal_position == "Center" and lane_index == 0):
                pyautogui.press('right')
                cv.putText(img, "Right", (5,img_height-10), cv.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
                lane_index += 1
        
        else:
                cv.putText(img, "Put your nose in the circle to start the game", (5,img_height-10), cv.FONT_HERSHEY_PLAIN, 3, (0,0,0), 2)
                cv.circle(img, (img_width//2, img_height//2), 100, (255,255,255), 3)

        Noss_Poss = check_circle(img, results)  
        # print(Noss_Poss)
        if (Noss_Poss == "Inside"):
        
            counter += 1
            # print(counter)
            if counter == num_of_frames:
            
                    # Command to Start the game first time.
                    #-------------------------------------

                if not(game_started):
                        game_started = True
                        cv.putText(img, "Game Started", (img_width//2,70), cv.FONT_HERSHEY_PLAIN, 3, (0,0,0), 3)
                        # print("Game Started")
                        NOS_CORR = results.pose_landmarks.landmark[mpPose.PoseLandmark.NOSE].y * img_height               

                        pyautogui.click(x=1300, y=800, button='left')

                # Command to resume the game after death of the character.
                #--------------------------------------------------------
                                
                # Otherwise if the game has started.                       
                else:
                    pyautogui.press('space')
                    print("Space")

                counter = 0

        # Otherwies if the nose is outside the circle.
        else:
                counter = 0

            # VERTICAL MOVEMENTS
            # --------------------

        if NOS_CORR:
            posture = check_up_down(img, results, NOS_CORR) 

            if posture == "Jumping":
                pyautogui.press('up')
                cv.putText(img, "Jump", (5,img_height-10), cv.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
                # print("Jump")
                jump_index += 1

            elif posture == "Rolling":
                pyautogui.press('down')
                # print("Roll")
                cv.putText(img, "Roll", (5,img_height-10), cv.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
                jump_index -= 1

            elif posture == "Standing" and jump_index != 1 :
                jump_index = 1

    else:
        counter = 0

    img = calculate_fps(img)

    cv.imshow('Subway Surfers using Head Movement', img)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cv.destroyAllWindows()
cam.release()

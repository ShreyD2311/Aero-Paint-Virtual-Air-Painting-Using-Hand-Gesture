import cv2
import time
import mediapipe as mp
import math

class handDetector():
    def __init__(self, image_mode= False, max_num_hands =1, modelC=1, min_detection_confidence =0.7, min_tracking_confidence =0.7):
        self.image_mode = image_mode
        self.max_num_hands = max_num_hands
        self.modelC = modelC
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        self.mphands = mp.solutions.hands
        self.hands = self.mphands.Hands(self.image_mode, self.max_num_hands, self.modelC, self.min_detection_confidence, self.min_tracking_confidence)
        self.mpdraw = mp.solutions.drawing_utils 
        self.finger_tip_id = [4,8,12,16,20]
        self.previous_palm_position = (0, 0)
        

    def findHands(self, img, draw =True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if  self.results.multi_hand_landmarks:
            for i in self.results.multi_hand_landmarks:
                if draw:
                    self.mpdraw.draw_landmarks(img, i , self.mphands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, hand_num =0, draw = True):
        self.lm_list=[]
        if self.results.multi_hand_landmarks:
            myHand= self.results.multi_hand_landmarks[hand_num]
            for id, lm in enumerate(myHand.landmark):
                #print(id, lm)
                h, w, c = img.shape
                cx,cy = int(lm.x*w), int(lm.y*h)
                self.lm_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, center=(cx,cy),radius=3, color=(255,255,255), thickness=1)
        return self.lm_list


    def calculate_angle(self, a, b, c): # Method to calculate the angle between three landmarks
        radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
        angle_degrees = abs(math.degrees(radians))
        return angle_degrees
        
    def calculate_distance(self, landmark1, landmark2):
        import math
        distance = math.sqrt((landmark1[1] - landmark2[1]) ** 2 +
                             (landmark1[2] - landmark2[2]) ** 2)
        return distance

    def fingerStatus(self):
        # Constants for angle thresholds
        thumb_angle_threshold = 90
        finger_angle_threshold = 45

        # Constants for distance thresholds
        thumb_distance_threshold = 30
        finger_distance_threshold = 25
        
        fingers = []
    
        # Check thumb status
        thumb_open1 = self.lm_list[self.finger_tip_id[0]][1] < self.lm_list[self.finger_tip_id[0] - 1][1]
        
        thumb_open2 = self.calculate_angle(
            self.lm_list[self.finger_tip_id[0] - 2],
            self.lm_list[self.finger_tip_id[0] - 1],
            self.lm_list[self.finger_tip_id[0]]
        ) > thumb_angle_threshold

        thumb_distance = self.calculate_distance(self.lm_list[self.finger_tip_id[0]],self.lm_list[0])
        thumb_open3 = thumb_distance > thumb_distance_threshold

        thumb_distance = self.calculate_distance(self.lm_list[self.finger_tip_id[3]],self.lm_list[self.finger_tip_id[4]])
        thumb_open4 = thumb_distance > 45
        thumb_open = thumb_open1 and thumb_open2 and (thumb_open3 or thumb_open4)
        fingers.append(1 if thumb_open else 0)
    
        # Check other fingers (indices 1 to 4)
        for i in range(1, 5):
            finger_open1 = self.lm_list[self.finger_tip_id[i]][2] < self.lm_list[self.finger_tip_id[i] - 2][2]

            finger_open2 = self.calculate_angle(
                self.lm_list[self.finger_tip_id[i] - 2],
                self.lm_list[self.finger_tip_id[i] - 1],
                self.lm_list[self.finger_tip_id[i]]
            ) > finger_angle_threshold

            finger_distance = self.calculate_distance(self.lm_list[self.finger_tip_id[i]],self.lm_list[0])
            finger_open3 = finger_distance > finger_distance_threshold

            finger_open = finger_open1 and finger_open2 and finger_open3
            fingers.append(1 if finger_open else 0)
    
        return fingers


    def detect_motion(self):
        current_palm_position = self.lm_list[0][1], self.lm_list[0][2]

        # Calculate the difference in X and Y coordinates
        dx = current_palm_position[0] - self.previous_palm_position[0]
        dy = current_palm_position[1] - self.previous_palm_position[1]

        # Determine the direction of motion
        direction = None
        if abs(dx) > abs(dy):
            if dx > 20:
                direction = "Right"
            elif dx < -20:
                direction = "Left"
        else:
            if dy > 20:
                direction = "Down"
            elif dy < -20:
                direction = "Up"

        self.previous_palm_position = current_palm_position

        return direction
    


def main():
    cap = cv2.VideoCapture(0)
    previousT = 0
    currentT= 0

    detector = handDetector()

    while True:
        ret, img = cap.read()

        img =detector.findHands(img, draw=True)
        landmark_list = detector.findPosition(img)
        if len(landmark_list)!=0:
            print(landmark_list[2])

        currentT = time.time()
        fps = 1/(currentT- previousT)
        previousT = currentT

        cv2.putText(img, 'Client FPS:' + str(int(fps)), (5,712), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2, color=(255,0,0))
        cv2.imshow('img', img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()

"""
import cv2
import time
import mediapipe as mp
import math

class HandDetector():
    def __init__(self, image_mode=False, max_num_hands=1, modelC=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.image_mode = image_mode
        self.max_num_hands = max_num_hands
        self.modelC = modelC
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        self.mphands = mp.solutions.hands
        self.hands = self.mphands.Hands(self.image_mode, self.max_num_hands, self.modelC, self.min_detection_confidence, self.min_tracking_confidence)
        self.mpdraw = mp.solutions.drawing_utils 
        self.finger_tip_id = [4, 8, 12, 16, 20]
        self.previous_palm_position = (0, 0)  # Initialize previous palm position

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for i in self.results.multi_hand_landmarks:
                if draw:
                    self.mpdraw.draw_landmarks(img, i, self.mphands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, hand_num=0, draw=True):
        self.lm_list = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[hand_num]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, center=(cx, cy), radius=3, color=(255, 255, 255), thickness=1)
        return self.lm_list

    def calculate_angle(self, a, b, c):  # Method to calculate the angle between three landmarks
        radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
        angle_degrees = abs(math.degrees(radians))
        return angle_degrees

    def calculate_distance(self, landmark1, landmark2):
        distance = math.sqrt((landmark1[1] - landmark2[1]) ** 2 +
                             (landmark1[2] - landmark2[2]) ** 2)
        return distance

    def detect_motion(self):
        current_palm_position = self.lm_list[0][1], self.lm_list[0][2]

        # Calculate the difference in X and Y coordinates
        dx = current_palm_position[0] - self.previous_palm_position[0]
        dy = current_palm_position[1] - self.previous_palm_position[1]

        # Determine the direction of motion
        direction = None
        if abs(dx) > abs(dy):
            if dx > 20:
                direction = "Right"
            elif dx < -20:
                direction = "Left"
        else:
            if dy > 20:
                direction = "Down"
            elif dy < -20:
                direction = "Up"

        self.previous_palm_position = current_palm_position

        return direction


def main():
    cap = cv2.VideoCapture(0)
    previousT = 0
    currentT = 0

    detector = HandDetector()

    while True:
        ret, img = cap.read()

        img = detector.findHands(img, draw=True)
        landmark_list = detector.findPosition(img)
        if len(landmark_list) != 0:
            motion_direction = detector.detect_motion()
            if motion_direction:
                print("Hand Motion Direction:", motion_direction)

        currentT = time.time()
        fps = 1 / (currentT - previousT)
        previousT = currentT

        cv2.putText(img, 'Client FPS:' + str(int(fps)), (5, 712), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2, color=(255, 0, 0))
        cv2.imshow('img', img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
"""
    

# def fingerStatus(self):
#     #if len(self.lm_list)!=0:    
#     fingers=[]

#     if (self.lm_list[self.finger_tip_id[0]][1] < self.lm_list[self.finger_tip_id[0] - 1][1]):
#         fingers.append(1)
#     else:
#         fingers.append(0)
    
#     for i in range(1,5):
#         if (self.lm_list[self.finger_tip_id[i]][2] < self.lm_list[self.finger_tip_id[i] - 2][2]):
#             fingers.append(1)
#         else:
#             fingers.append(0)
            
#     return fingers





# def fingerStatus(self):
#     fingers = []

#     # Check the status of the thumb (index 0)
#     thumb_open = self.calculate_angle(
#         self.lm_list[self.finger_tip_id[0] - 2],
#         self.lm_list[self.finger_tip_id[0] - 1],
#         self.lm_list[self.finger_tip_id[0]]
#     ) > thumb_angle_threshold

#     fingers.append(1 if thumb_open else 0)

#     # Check the status of the other four fingers (indices 1 to 4)
#     for i in range(1, 5):
#         finger_open = self.calculate_angle(
#             self.lm_list[self.finger_tip_id[i] - 2],
#             self.lm_list[self.finger_tip_id[i] - 1],
#             self.lm_list[self.finger_tip_id[i]]
#         ) > finger_angle_threshold

#         fingers.append(1 if finger_open else 0)

#     return fingers


# def fingerStatus(self):
#     fingers = []

#     # Check the status of the thumb (index 0)
#     thumb_distance = self.calculate_distance(
#         self.lm_list[self.finger_tip_id[0]],
#         self.lm_list[self.palm_landmark_id]
#     )
#     thumb_open = thumb_distance > thumb_distance_threshold

#     fingers.append(1 if thumb_open else 0)

#     # Check the status of the other four fingers (indices 1 to 4)
#     for i in range(1, 5):
#         finger_distance = self.calculate_distance(
#             self.lm_list[self.finger_tip_id[i]],
#             self.lm_list[self.palm_landmark_id]
#         )
#         finger_open = finger_distance > finger_distance_threshold

#         fingers.append(1 if finger_open else 0)

#     return fingers









"""
import cv2
import time
import mediapipe as mp 

class handDetector():
    def __init__(self, image_mode= False, max_num_hands =3, modelC=1, min_detection_confidence =0.5, min_tracking_confidence =0.5):
        self.image_mode = image_mode
        self.max_num_hands = max_num_hands
        self.modelC = modelC
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        self.mphands= mp.solutions.hands
        self.hands = self.mphands.Hands(self.image_mode, self.max_num_hands, self.modelC, self.min_detection_confidence, self.min_tracking_confidence)
        self.mpdraw = mp.solutions.drawing_utils 
        self.finger_tip_id= [4,8,12,16,20]
        

    def findHands(self, img, draw =True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if  self.results.multi_hand_landmarks:
            for i in self.results.multi_hand_landmarks:
                if draw:
                    self.mpdraw.draw_landmarks(img, i , self.mphands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, hand_num =0, draw = True):
        self.lm_list=[]
        if self.results.multi_hand_landmarks:
            myHand= self.results.multi_hand_landmarks[hand_num]
            for id, lm in enumerate(myHand.landmark):
                #print(id, lm)
                h, w, c = img.shape
                cx,cy = int(lm.x*w), int(lm.y*h)
                self.lm_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, center=(cx,cy),radius=3, color=(255,255,255), thickness=1)
        return self.lm_list

    def fingerStatus(self):
        #if len(self.lm_list)!=0:    
        fingers=[]

        if (self.lm_list[self.finger_tip_id[0]][1] < self.lm_list[self.finger_tip_id[0] - 1][1]):
            fingers.append(1)
        else:
            fingers.append(0)
        
        for i in range(1,5):
            if (self.lm_list[self.finger_tip_id[i]][2] < self.lm_list[self.finger_tip_id[i] - 2][2]):
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers


def main():
    cap = cv2.VideoCapture(0)
    previousT = 0
    currentT= 0

    detector = handDetector()

    while True:
        ret, img = cap.read()

        img =detector.findHands(img, draw=True)
        landmark_list = detector.findPosition(img)
        if len(landmark_list)!=0:
            print(landmark_list[2])

        currentT = time.time()
        fps = 1/(currentT- previousT)
        previousT = currentT

        cv2.putText(img, 'Client FPS:' + str(int(fps)), (10,70), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2, color=(255,0,0))
        cv2.imshow('img', img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
"""
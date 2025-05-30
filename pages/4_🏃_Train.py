import streamlit as st
import json
import requests 
import cv2
from cvzone.PoseModule import PoseDetector
import math
import numpy as np
import plotly.graph_objects as go
import tempfile

# Initialize session state variables
def initialize_session_state():
    if 'type' not in st.session_state:
        st.session_state.type = None
    if 'counter1' not in st.session_state:
        st.session_state.counter1 = 0
    if 'counter2' not in st.session_state:
        st.session_state.counter2 = 0
    if 'counter3' not in st.session_state:
        st.session_state.counter3 = 0
    if 'counter4' not in st.session_state:
        st.session_state.counter4 = 0
    if 'counter5' not in st.session_state:
        st.session_state.counter5 = 0

# Initialize session state
initialize_session_state()

# Header
html = """
<div style="background-color:#025246 ;padding:10px">
<h2 style="color:white;text-align:center;">Train here</h2>
</div>"""
st.markdown(html, unsafe_allow_html=True)

# Sidebar for exercise selection
app_mode = st.sidebar.selectbox("Choose the exercise", ["About","Left Dumbbell","Right Dumbbell","Squats","Pushups","Shoulder press"])

if app_mode == "About":
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("## Welcome to the Training arena")
        st.markdown("Choose the workout you wish to do from the sidebar")
        st.write("##")
        st.write("""
        Here are few general instructions to follow while doing the workout:

        - It is necessary for you to provide web cam access. If you do not have a webcam, kindly attach an external camera while performing exercises.
        - Please avoid crowded places as the model can only detect 1 person. 
        - Please ensure that the surrounding is well lit so that the camera can detect you.
        - Please make sure the camera is focused on you based on the exercise so that the system can detect the angles and give you the correct input on form and count reps.

        With all that out of the way, Its time for you to get pumped up
        """)

    with col2:
        try:
            st.image('./gif/ham.gif')
        except:
            st.write("Animation placeholder - gif file not found")

elif app_mode == "Left Dumbbell":
    st.markdown("## Left Dumbbell")
    weight1 = st.slider('What is your weight?', 20, 130, 40)
    st.write("I'm ", weight1, 'kgs')
    st.write("-------------")
    goal_calorie1 = st.slider('Set a goal calorie to burn', 1, 200, 15)
    st.write("I want to burn", goal_calorie1, 'kcal')
    st.write("-------------")
    st.write(" Click on the Start button to start the live video feed.")
    st.write("##")
    
    class AngleFinder:
        def __init__(self, lmlist, p1, p2, p3, drawPoints):
            self.lmlist = lmlist
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
            self.drawPoints = drawPoints

        def angle(self, img):
            if len(self.lmlist) != 0:
                try:
                    point1 = self.lmlist[self.p1]
                    point2 = self.lmlist[self.p2]
                    point3 = self.lmlist[self.p3]
                    
                    x1, y1 = point1[1:3]
                    x2, y2 = point2[1:3]
                    x3, y3 = point3[1:3]
                    
                    # calculating angle for left arm
                    leftHandAngle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                                                math.atan2(y1 - y2, x1 - x2))
                    
                    leftHandAngle = int(np.interp(leftHandAngle, [42, 143], [100, 0]))
                    
                    # drawing circles and lines on selected points
                    if self.drawPoints:
                        cv2.circle(img, (x1, y1), 10, (0, 255, 255), 5)
                        cv2.circle(img, (x1, y1), 15, (0, 255, 0), 6)
                        cv2.circle(img, (x2, y2), 10, (0, 255, 255), 5)
                        cv2.circle(img, (x2, y2), 15, (0, 255, 0), 6)
                        cv2.circle(img, (x3, y3), 10, (0, 255, 255), 5)
                        cv2.circle(img, (x3, y3), 15, (0, 255, 0), 6)
                        
                        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
                        cv2.line(img, (x2, y2), (x3, y3), (0, 0, 255), 4)
                    
                    return leftHandAngle
                except (IndexError, TypeError):
                    return 0
            return 0

    def handle_click_start():
        st.session_state.type = "Start"

    def handle_click_stop():
        st.session_state.type = "Stop"
    
    start_button = st.button('Start', on_click=handle_click_start)
    stop_button = st.button('Stop', on_click=handle_click_stop)
    
    # defining some variables
    counter = 0
    direction = 0
    frame_placeholder = st.empty()
    detector = PoseDetector(detectionCon=0.7, trackCon=0.7)
    
    if st.session_state['type'] == 'Start':
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open camera. Please check your camera connection.")
        else:
            while cap.isOpened() and st.session_state['type'] == 'Start':
                ret, img = cap.read()
                if not ret:
                    st.error("Failed to read from camera")
                    break
                    
                img = cv2.resize(img, (640, 480))
                detector.findPose(img, draw=0)
                lmList, bboxInfo = detector.findPosition(img, bboxWithHands=0, draw=False)
                
                angle1 = AngleFinder(lmList, 11, 13, 15, drawPoints=True)
                left = angle1.angle(img)
                
                # Counting number of reps
                if left >= 90:
                    if direction == 0:
                        counter += 0.5
                        st.session_state.counter1 = counter
                        direction = 1
                if left <= 70:
                    if direction == 1:
                        counter += 0.5
                        st.session_state.counter1 = counter
                        direction = 0
                
                # putting scores on the screen
                cv2.rectangle(img, (0, 0), (120, 120), (255, 0, 0), -1)
                cv2.putText(img, str(int(counter)), (1, 70), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.6, (0, 0, 255), 6)
                
                # Converting values for rectangles
                leftval = np.interp(left, [0, 100], [480, 280])
                
                # Drawing left rectangle and putting text
                cv2.rectangle(img, (582, 280), (632, 480), (0, 0, 255), 5)
                cv2.rectangle(img, (582, int(leftval)), (632, 480), (0, 0, 255), -1)
                
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(img, "RGB")
                
            cap.release()
            
    elif st.session_state['type'] == 'Stop': 
        st.write("The video capture has ended")
        st.write("---------")
        st.write("## Analytics") 
        st.write("You did", st.session_state.counter1, "reps")   
        
        calories1 = 0.25 * st.session_state.counter1
        if calories1 < goal_calorie1:
            st.write("You have burned", calories1, "kcal of calories")
            st.write("You have not achieved your goal. Try again")
        else:
            st.write("You have burned", calories1, "kcal of calories")
            st.write("You have achieved your goal. Congratulations")
        
        fig = go.Figure(data=[go.Bar(x=['Bicep Curls'], y=[calories1], name='Calories Burned')])
        fig.add_trace(go.Bar(x=['Bicep Curls'], y=[goal_calorie1], name='Goal Calorie'))
        fig.update_layout(
            title='Calories Burned for Bicep Curls',
            xaxis_title='Exercise',
            yaxis_title='Calories Burned'
        )
        st.plotly_chart(fig)

elif app_mode == "Right Dumbbell":
    st.markdown("## Right Dumbbell")
    weight2 = st.slider('What is your weight?', 20, 130, 40)
    st.write(f"I'm {weight2} kgs")
    st.write("-------------")
    goal_calorie2 = st.slider('Set a goal calorie to burn', 1, 200, 15)
    st.write(f"I want to burn {goal_calorie2} kcal")
    st.write("-------------")
    st.write("Click on the Start button to start the live video feed.")
    st.write("##")

    # Define AngleFinder for right dumbbell
    class AngleFinder:
        def __init__(self, lmlist, p1, p2, p3, drawPoints):
            self.lmlist = lmlist
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
            self.drawPoints = drawPoints

        def angle(self, img):
            if len(self.lmlist) != 0:
                try:
                    x1, y1 = self.lmlist[self.p1][1:3]
                    x2, y2 = self.lmlist[self.p2][1:3]
                    x3, y3 = self.lmlist[self.p3][1:3]

                    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                                         math.atan2(y1 - y2, x1 - x2))
                    angle = int(np.interp(angle, [42, 143], [100, 0]))

                    if self.drawPoints:
                        for (x, y) in [(x1, y1), (x2, y2), (x3, y3)]:
                            cv2.circle(img, (x, y), 10, (0, 255, 255), 5)
                            cv2.circle(img, (x, y), 15, (0, 255, 0), 6)
                        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
                        cv2.line(img, (x2, y2), (x3, y3), (0, 0, 255), 4)

                    return angle
                except Exception:
                    return 0
            return 0

    def handle_click_start():
        st.session_state.type = "Start2"

    def handle_click_stop():
        st.session_state.type = "Stop2"

    st.button('Start', on_click=handle_click_start)
    st.button('Stop', on_click=handle_click_stop)

    if "counter2" not in st.session_state:
        st.session_state.counter2 = 0
    if "direction2" not in st.session_state:
        st.session_state.direction2 = 0

    frame_placeholder = st.empty()
    detector = PoseDetector(detectionCon=0.7, trackCon=0.7)

    if st.session_state['type'] == 'Start2':
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open camera. Please check your camera connection.")
        else:
            while cap.isOpened() and st.session_state['type'] == 'Start2':
                ret, img = cap.read()
                if not ret:
                    st.error("Failed to read from camera")
                    break

                img = cv2.resize(img, (640, 480))
                detector.findPose(img, draw=False)
                lmList, _ = detector.findPosition(img, bboxWithHands=False, draw=False)

                angle_tracker = AngleFinder(lmList, 12, 14, 16, drawPoints=True)
                right = angle_tracker.angle(img)

                # Rep counting logic
                if right >= 90:
                    if st.session_state.direction2 == 0:
                        st.session_state.counter2 += 0.5
                        st.session_state.direction2 = 1
                if right <= 70:
                    if st.session_state.direction2 == 1:
                        st.session_state.counter2 += 0.5
                        st.session_state.direction2 = 0

                # Display rep count
                cv2.rectangle(img, (0, 0), (120, 120), (255, 0, 0), -1)
                cv2.putText(img, str(int(st.session_state.counter2)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

                # Progress bar
                bar_val = np.interp(right, [0, 100], [480, 280])
                cv2.rectangle(img, (582, 280), (632, 480), (0, 0, 255), 5)
                cv2.rectangle(img, (582, int(bar_val)), (632, 480), (0, 0, 255), -1)

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(img, "RGB")

            cap.release()

    elif st.session_state['type'] == 'Stop2':
        st.write("The video capture has ended")
        st.write("---------")
        st.write("## Analytics")
        st.write(f"You did {st.session_state.counter2} reps")

        calories2 = 0.25 * st.session_state.counter2
        st.write(f"You have burned {calories2:.2f} kcal of calories")

        if calories2 < goal_calorie2:
            st.warning("You have not achieved your goal. Try again!")
        else:
            st.success("You have achieved your goal. Congratulations!")

        fig = go.Figure(data=[
            go.Bar(x=['Right Bicep Curls'], y=[calories2], name='Calories Burned'),
            go.Bar(x=['Right Bicep Curls'], y=[goal_calorie2], name='Goal Calorie')
        ])
        fig.update_layout(
            title='Calories Burned for Right Bicep Curls',
            xaxis_title='Exercise',
            yaxis_title='Calories Burned'
        )
        st.plotly_chart(fig)

elif app_mode == "Squats":
    st.markdown("## Squats")
    weight3 = st.slider('What is your weight?', 20, 130, 40)
    st.write("I'm ", weight3, 'kgs')
    st.write("-------------")
    goal_calorie3 = st.slider('Set a goal calorie to burn', 1, 200, 15)
    st.write("I want to burn", goal_calorie3, 'kcal')
    st.write("-------------")
    st.write(" Click on the Start button to start the live video feed.")
    st.write("##")

    class AngleFinder:
        def __init__(self, lmlist, p1, p2, p3, p4, p5, p6, drawPoints):
            self.lmlist = lmlist
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
            self.p4 = p4
            self.p5 = p5
            self.p6 = p6
            self.drawPoints = drawPoints

        def angle(self, img):
            if len(self.lmlist) != 0:
                try:
                    points = [self.lmlist[p] for p in [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6]]
                    coords = [(p[1], p[2]) for p in points]
                    
                    x1, y1 = coords[0]
                    x2, y2 = coords[1]
                    x3, y3 = coords[2]
                    x4, y4 = coords[3]
                    x5, y5 = coords[4]
                    x6, y6 = coords[5]
                    
                    # calculating angle for left leg
                    leftLegAngle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                                               math.atan2(y1 - y2, x1 - x2))
                    
                    leftLegAngle = int(np.interp(leftLegAngle, [42, 143], [100, 0]))
                    
                    # drawing circles and lines on selected points
                    if self.drawPoints:
                        for x, y in coords:
                            cv2.circle(img, (x, y), 10, (0, 255, 255), 5)
                            cv2.circle(img, (x, y), 15, (0, 255, 0), 6)
                        
                        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
                        cv2.line(img, (x2, y2), (x3, y3), (0, 0, 255), 4)
                        cv2.line(img, (x4, y4), (x5, y5), (0, 0, 255), 4)
                        cv2.line(img, (x5, y5), (x6, y6), (0, 0, 255), 4)
                        cv2.line(img, (x1, y1), (x4, y4), (0, 0, 255), 4)
                    
                    return leftLegAngle
                except (IndexError, TypeError):
                    return 0
            return 0

    def handle_click_start():
        st.session_state.type = "Start3"

    def handle_click_stop():
        st.session_state.type = "Stop3"
    
    start_button = st.button('Start', on_click=handle_click_start)
    stop_button = st.button('Stop', on_click=handle_click_stop)
    
    counter = 0
    direction = 0
    frame_placeholder = st.empty()
    detector = PoseDetector(detectionCon=0.7, trackCon=0.7)
    
    if st.session_state['type'] == 'Start3':
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open camera. Please check your camera connection.")
        else:
            while cap.isOpened() and st.session_state['type'] == 'Start3':
                ret, img = cap.read()
                if not ret:
                    st.error("Failed to read from camera")
                    break
                    
                img = cv2.resize(img, (640, 480))
                detector.findPose(img, draw=0)
                lmList, bboxInfo = detector.findPosition(img, bboxWithHands=0, draw=False)
                
                angle1 = AngleFinder(lmList, 24, 26, 28, 23, 25, 27, drawPoints=True)
                left = angle1.angle(img)
                
                # Counting number of reps
                if left >= 90:
                    if direction == 0:
                        counter += 0.5
                        st.session_state.counter3 = counter
                        direction = 1
                if left <= 70:
                    if direction == 1:
                        counter += 0.5
                        st.session_state.counter3 = counter
                        direction = 0
                
                # putting scores on the screen
                cv2.rectangle(img, (0, 0), (120, 120), (255, 0, 0), -1)
                cv2.putText(img, str(int(counter)), (1, 70), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.6, (0, 0, 255), 6)
                
                # Converting values for rectangles
                leftval = np.interp(left, [0, 100], [480, 280])
                
                # Drawing rectangle
                cv2.rectangle(img, (582, 280), (632, 480), (0, 0, 255), 5)
                cv2.rectangle(img, (582, int(leftval)), (632, 480), (0, 0, 255), -1)
                
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(img, "RGB")
                
            cap.release()
            
    elif st.session_state['type'] == 'Stop3': 
        st.write("The video capture has ended")
        st.write("---------")
        st.write("## Analytics") 
        st.write("You did", st.session_state.counter3, "reps")   
        
        calories3 = 0.3 * st.session_state.counter3
        if calories3 < goal_calorie3:
            st.write("You have burned", calories3, "kcal of calories")
            st.write("You have not achieved your goal. Try again")
        else:
            st.write("You have burned", calories3, "kcal of calories")
            st.write("You have achieved your goal. Congratulations")
        
        fig = go.Figure(data=[go.Bar(x=['Squats'], y=[calories3], name='Calories Burned')])
        fig.add_trace(go.Bar(x=['Squats'], y=[goal_calorie3], name='Goal Calorie'))
        fig.update_layout(
            title='Calories Burned for Squats',
            xaxis_title='Exercise',
            yaxis_title='Calories Burned'
        )
        st.plotly_chart(fig)

elif app_mode == "Pushups":
    st.markdown("## Pushups")
    weight4 = st.slider('What is your weight?', 20, 130, 40)
    st.write("I'm ", weight4, 'kgs')
    st.write("-------------")
    goal_calorie4 = st.slider('Set a goal calorie to burn', 1, 200, 15)
    st.write("I want to burn", goal_calorie4, 'kcal')
    st.write("-------------")
    st.write(" Click on the Start button to start the live video feed.")
    st.write("##")

    def angles(lmlist, p1, p2, p3, p4, p5, p6, drawpoints, img):
        if len(lmlist) != 0:
            try:
                points = [lmlist[p] for p in [p1, p2, p3, p4, p5, p6]]
                coords = [(p[1], p[2]) for p in points]
                
                x1, y1 = coords[0]
                x2, y2 = coords[1]
                x3, y3 = coords[2]
                x4, y4 = coords[3]
                x5, y5 = coords[4]
                x6, y6 = coords[5]

                if drawpoints:
                    for x, y in coords:
                        cv2.circle(img, (x, y), 10, (255, 0, 255), 5)
                        cv2.circle(img, (x, y), 15, (0, 255, 0), 5)

                    cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 6)
                    cv2.line(img, (x2, y2), (x3, y3), (0, 0, 255), 6)
                    cv2.line(img, (x4, y4), (x5, y5), (0, 0, 255), 6)
                    cv2.line(img, (x5, y5), (x6, y6), (0, 0, 255), 6)
                    cv2.line(img, (x1, y1), (x4, y4), (0, 0, 255), 6)

                lefthandangle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                                            math.atan2(y1 - y2, x1 - x2))

                righthandangle = math.degrees(math.atan2(y6 - y5, x6 - x5) -
                                             math.atan2(y4 - y5, x4 - x5))

                leftHandAngle = int(np.interp(lefthandangle, [-30, 180], [100, 0]))
                rightHandAngle = int(np.interp(righthandangle, [34, 173], [100, 0]))

                return leftHandAngle, rightHandAngle
            except (IndexError, TypeError):
                return 0, 0
        return 0, 0

    def handle_click_start():
        st.session_state.type = "Start4"

    def handle_click_stop():
        st.session_state.type = "Stop4"
    
    start_button = st.button('Start', on_click=handle_click_start)
    stop_button = st.button('Stop', on_click=handle_click_stop)
    
    counter = 0
    direction = 0
    frame_placeholder = st.empty()
    pd = PoseDetector(detectionCon=0.7, trackCon=0.7)
    
    if st.session_state['type'] == 'Start4':
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open camera. Please check your camera connection.")
        else:
            while cap.isOpened() and st.session_state['type'] == 'Start4':
                ret, img = cap.read()
                if not ret:
                    st.error("Failed to read from camera")
                    break
                    
                img = cv2.resize(img, (1000, 500))
                pd.findPose(img, draw=0)
                lmlist, bbox = pd.findPosition(img, draw=0, bboxWithHands=0)
                
                left, right = angles(lmlist, 11, 13, 15, 12, 14, 16, drawpoints=1, img=img)
                
                if left >= 60 and right >= 60:
                    if direction == 0:
                        counter += 0.5
                        st.session_state.counter4 = counter
                        direction = 1
                if left <= 60 and right <= 60:
                    if direction == 1:
                        counter += 0.5
                        st.session_state.counter4 = counter
                        direction = 0

                cv2.rectangle(img, (0, 0), (120, 120), (255, 0, 0), -1)
                cv2.putText(img, str(int(counter)), (20, 70), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.6, (0, 0, 255), 7)

                leftval = np.interp(right, [0, 100], [400, 200])
                rightval = np.interp(right, [0, 100], [400, 200])

                cv2.putText(img, 'R', (24, 195), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 255), 7)
                cv2.rectangle(img, (8, 200), (50, 400), (0, 255, 0), 5)
                cv2.rectangle(img, (8, int(rightval)), (50, 400), (255, 0, 0), -1)

                cv2.putText(img, 'L', (962, 195), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 255), 7)
                cv2.rectangle(img, (952, 200), (995, 400), (0, 255, 0), 5)
                cv2.rectangle(img, (952, int(leftval)), (995, 400), (255, 0, 0), -1)

                if left > 70:
                    cv2.rectangle(img, (952, int(leftval)), (995, 400), (0, 0, 255), -1)

                if right > 70:
                    cv2.rectangle(img, (8, int(leftval)), (50, 400), (0, 0, 255), -1)

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(img, "RGB")

                
elif app_mode == "Shoulder press":
    st.markdown("## Shoulder Press")
    weight5 = st.slider('What is your weight?', 20, 130, 40)
    st.write("I'm ", weight5, 'kgs')
    st.write("-------------")
    goal_calorie5 = st.slider('Set a goal calorie to burn', 1, 200, 15)
    st.write("I want to burn", goal_calorie5, 'kcal')
    st.write("-------------")
    st.write(" Click on the Start button to start the live video feed.")
    st.write("##")

    class AngleFinder:
        def __init__(self, lmlist, p1, p2, p3, p4, p5, p6, drawPoints):
            self.lmlist = lmlist
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
            self.p4 = p4
            self.p5 = p5
            self.p6 = p6
            self.drawPoints = drawPoints

        def angle(self, img):
            if len(self.lmlist) != 0:
                try:
                    coords = [(self.lmlist[i][1], self.lmlist[i][2]) for i in [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6]]
                    x1, y1 = coords[0]
                    x2, y2 = coords[1]
                    x3, y3 = coords[2]
                    x4, y4 = coords[3]
                    x5, y5 = coords[4]
                    x6, y6 = coords[5]

                    leftAngle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                                             math.atan2(y1 - y2, x1 - x2))
                    rightAngle = math.degrees(math.atan2(y6 - y5, x6 - x5) -
                                              math.atan2(y4 - y5, x4 - x5))

                    leftMapped = int(np.interp(leftAngle, [-170, 180], [100, 0]))
                    rightMapped = int(np.interp(rightAngle, [-170, 180], [100, 0]))

                    if self.drawPoints:
                        for x, y in coords:
                            cv2.circle(img, (x, y), 10, (0, 255, 255), 5)
                            cv2.circle(img, (x, y), 15, (0, 255, 0), 6)

                        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 4)
                        cv2.line(img, (x2, y2), (x3, y3), (255, 0, 0), 4)
                        cv2.line(img, (x4, y4), (x5, y5), (0, 0, 255), 4)
                        cv2.line(img, (x5, y5), (x6, y6), (0, 0, 255), 4)

                    return leftMapped, rightMapped
                except (IndexError, TypeError):
                    return 0, 0
            return 0, 0

    def handle_click_start():
        st.session_state.type = "Start5"

    def handle_click_stop():
        st.session_state.type = "Stop5"

    st.button('Start', on_click=handle_click_start)
    st.button('Stop', on_click=handle_click_stop)

    counter = 0
    direction = 0
    frame_placeholder = st.empty()
    detector = PoseDetector(detectionCon=0.7, trackCon=0.7)

    if st.session_state['type'] == 'Start5':
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open camera. Please check your camera connection.")
        else:
            while cap.isOpened() and st.session_state['type'] == 'Start5':
                ret, img = cap.read()
                if not ret:
                    st.error("Failed to read from camera")
                    break

                img = cv2.resize(img, (960, 540))
                detector.findPose(img, draw=False)
                lmlist, bbox = detector.findPosition(img, bboxWithHands=False, draw=False)

                af = AngleFinder(lmlist, 11, 13, 15, 12, 14, 16, drawPoints=True)
                left, right = af.angle(img)

                if left >= 80 and right >= 80:
                    if direction == 0:
                        counter += 0.5
                        st.session_state.counter5 = counter
                        direction = 1
                if left <= 60 and right <= 60:
                    if direction == 1:
                        counter += 0.5
                        st.session_state.counter5 = counter
                        direction = 0

                cv2.rectangle(img, (0, 0), (120, 120), (255, 0, 0), -1)
                cv2.putText(img, str(int(counter)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 6)

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(img, "RGB")

            cap.release()

    elif st.session_state['type'] == 'Stop5':
        st.write("The video capture has ended")
        st.write("---------")
        st.write("## Analytics")
        st.write("You did", st.session_state.counter5, "reps")

        calories5 = 0.22 * st.session_state.counter5
        if calories5 < goal_calorie5:
            st.write("You have burned", calories5, "kcal of calories")
            st.write("You have not achieved your goal. Try again")
        else:
            st.write("You have burned", calories5, "kcal of calories")
            st.write("You have achieved your goal. Congratulations")

        fig = go.Figure(data=[go.Bar(x=['Shoulder Press'], y=[calories5], name='Calories Burned')])
        fig.add_trace(go.Bar(x=['Shoulder Press'], y=[goal_calorie5], name='Goal Calorie'))
        fig.update_layout(
            title='Calories Burned for Shoulder Press',
            xaxis_title='Exercise',
            yaxis_title='Calories Burned'
        )
        st.plotly_chart(fig)

elif app_mode == "Shoulder press":
    st.markdown("## Shoulder Press")
    weight5 = st.slider('What is your weight?', 20, 130, 40)
    st.write("I'm ", weight5, 'kgs')
    st.write("-------------")
    goal_calorie5 = st.slider('Set a goal calorie to burn', 1, 200, 15)
    st.write("I want to burn", goal_calorie5, 'kcal')
    st.write("-------------")
    st.write(" Click on the Start button to start the live video feed.")
    st.write("##")

    class AngleFinder:
        def __init__(self, lmlist, p1, p2, p3, p4, p5, p6, drawPoints):
            self.lmlist = lmlist
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
            self.p4 = p4
            self.p5 = p5
            self.p6 = p6
            self.drawPoints = drawPoints

        def angle(self, img):
            if len(self.lmlist) != 0:
                try:
                    coords = [(self.lmlist[i][1], self.lmlist[i][2]) for i in [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6]]
                    x1, y1 = coords[0]
                    x2, y2 = coords[1]
                    x3, y3 = coords[2]
                    x4, y4 = coords[3]
                    x5, y5 = coords[4]
                    x6, y6 = coords[5]

                    leftAngle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                                             math.atan2(y1 - y2, x1 - x2))
                    rightAngle = math.degrees(math.atan2(y6 - y5, x6 - x5) -
                                              math.atan2(y4 - y5, x4 - x5))

                    leftMapped = int(np.interp(leftAngle, [-170, 180], [100, 0]))
                    rightMapped = int(np.interp(rightAngle, [-170, 180], [100, 0]))

                    if self.drawPoints:
                        for x, y in coords:
                            cv2.circle(img, (x, y), 10, (0, 255, 255), 5)
                            cv2.circle(img, (x, y), 15, (0, 255, 0), 6)

                        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 4)
                        cv2.line(img, (x2, y2), (x3, y3), (255, 0, 0), 4)
                        cv2.line(img, (x4, y4), (x5, y5), (0, 0, 255), 4)
                        cv2.line(img, (x5, y5), (x6, y6), (0, 0, 255), 4)

                    return leftMapped, rightMapped
                except (IndexError, TypeError):
                    return 0, 0
            return 0, 0

    def handle_click_start():
        st.session_state.type = "Start5"

    def handle_click_stop():
        st.session_state.type = "Stop5"

    st.button('Start', on_click=handle_click_start)
    st.button('Stop', on_click=handle_click_stop)

    counter = 0
    direction = 0
    frame_placeholder = st.empty()
    detector = PoseDetector(detectionCon=0.7, trackCon=0.7)

    if st.session_state['type'] == 'Start5':
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open camera. Please check your camera connection.")
        else:
            while cap.isOpened() and st.session_state['type'] == 'Start5':
                ret, img = cap.read()
                if not ret:
                    st.error("Failed to read from camera")
                    break

                img = cv2.resize(img, (960, 540))
                detector.findPose(img, draw=False)
                lmlist, bbox = detector.findPosition(img, bboxWithHands=False, draw=False)

                af = AngleFinder(lmlist, 11, 13, 15, 12, 14, 16, drawPoints=True)
                left, right = af.angle(img)

                if left >= 80 and right >= 80:
                    if direction == 0:
                        counter += 0.5
                        st.session_state.counter5 = counter
                        direction = 1
                if left <= 60 and right <= 60:
                    if direction == 1:
                        counter += 0.5
                        st.session_state.counter5 = counter
                        direction = 0

                cv2.rectangle(img, (0, 0), (120, 120), (255, 0, 0), -1)
                cv2.putText(img, str(int(counter)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 6)

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(img, "RGB")

            cap.release()

    elif st.session_state['type'] == 'Stop5':
        st.write("The video capture has ended")
        st.write("---------")
        st.write("## Analytics")
        st.write("You did", st.session_state.counter5, "reps")

        calories5 = 0.22 * st.session_state.counter5
        if calories5 < goal_calorie5:
            st.write("You have burned", calories5, "kcal of calories")
            st.write("You have not achieved your goal. Try again")
        else:
            st.write("You have burned", calories5, "kcal of calories")
            st.write("You have achieved your goal. Congratulations")

        fig = go.Figure(data=[go.Bar(x=['Shoulder Press'], y=[calories5], name='Calories Burned')])
        fig.add_trace(go.Bar(x=['Shoulder Press'], y=[goal_calorie5], name='Goal Calorie'))
        fig.update_layout(
            title='Calories Burned for Shoulder Press',
            xaxis_title='Exercise',
            yaxis_title='Calories Burned'
        )
        st.plotly_chart(fig)

import cv2
import numpy as np

lk_params = dict(winSize=(10, 10),
                 maxLevel=2,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))



def selected_point(event, x, y, flags, params):
    global point, point_selected, old_points
    if event == cv2.EVENT_LBUTTONDOWN:
        point = (x, y)
        point_selected = True
        old_points = np.array([[x, y]], dtype=np.float32)



def rescale_frame(frame, scale=0.75):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)

    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)


cap = cv2.VideoCapture("test1.mp4")

ret, frame1 = cap.read()
ret, frame2 = cap.read()
old_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)


cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", selected_point)
point_selected = False

point = ()
old_points = np.array([[]])

while cap.isOpened():

    diff = cv2.absdiff(frame1, frame2)

    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=5)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    gray_frame = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    for contour in contours:
        i =1
        (x, y, w, h) = cv2.boundingRect(contour)
        if cv2.contourArea(contour) > 4000:
            continue
        if point_selected is True:
            new_points, status, error = cv2.calcOpticalFlowPyrLK(old_gray, gray_frame, old_points, None, **lk_params)
            old_gray = gray_frame.copy()
            old_points = new_points
            # print(new_points)
            x_, y_ = new_points.ravel()
            if (abs(x-x_) <= 25) & (abs(y-y_ <=25)) :
                p1 = x_
                p2 = y_
                cv2.circle(frame1, ((int)(x_), (int)(y_)), 5, (0, 255, 0), -1)
                cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame1, "tracking", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40,235, 249), 2)

                x_y_coor = "track X: " +  str(x_)  + ", strack Y: " + '_' + str(y_)
                cv2.putText(frame1, x_y_coor, (100,150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (40, 235, 249), 2)

                center = "image center: " + str(frame1.shape[1]//2) +" , "+ str(frame1.shape[0]//2)
                cv2.putText(frame1, center, (100,100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (40, 235, 249), 2)

                center_ = "move X: " + str((frame1.shape[1]//2) - x_) + ", move Y: " + str((frame1.shape[0]//2)-x_)
                cv2.putText(frame1, center_, (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (40, 235, 249), 2)


            else :
                old_gray = gray_frame.copy()
                old_points = new_points
                # print(new_points)
                x_, y_ = new_points.ravel()
                p1 = x_
                p2 = y_
                cv2.circle(frame1, ((int)(x_), (int)(y_)), 5, (50, 50, 100), -1)

        else :
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame1, 'Movement Found!', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.drawContours(frame1, contours, -1, (0,255,0), 2)

    frame_resized = rescale_frame(frame1, scale=0.5)
    cv2.imshow("Frame", frame1)

    frame1 = frame2
    ret, frame2 = cap.read()
    # point_selected = False
    if cv2.waitKey(40) == 27:
        break

cap.release()
cv2.destroyAllWindows()

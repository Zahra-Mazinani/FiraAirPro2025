import cv2
import numpy as np

# Initialize camera
cap = cv2.VideoCapture(0)


H_template = cv2.imread('H.png',0)
H_template = cv2.resize(H_template, (50, 50))  # Resize ROI to match template size


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to get a binary image
    _, binary = cv2.threshold(gray, 100, 200, cv2.THRESH_BINARY_INV)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    found_H = False
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 10 and h > 10:  # Filter small contours
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, (50, 50))  # Resize ROI to match template size
            roi= np.bitwise_not(roi)

            # Apply template matching
            res = cv2.matchTemplate(roi, H_template, cv2.TM_CCOEFF_NORMED)
            if res >= 0.46:  # Adjust the threshold as needed
                found_H = True
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Found 'H'!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                break
    

    if not found_H:
        cv2.putText(frame, "'H' not found", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Display the frame
    cv2.imshow('Frame', frame)


    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
import random
from tkinter import messagebox
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

detector = HandDetector(maxHands=1)
timer = 0
stateResult = False
startGame = True
scores = [0, 0]  # [AI, Player]
roundCooldown = 2  # seconds to wait before next round
lastRoundTime = time.time()
imgAI = None  # Placeholder for AI move image

while True:
    imgBG = cv2.imread("Resources/BG.png")
    success, img = cap.read()

    imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
    imgScaled = imgScaled[:, 80:480]

    # Detect hands
    hands, img = detector.findHands(imgScaled)

    currentTime = time.time()

    # Start a new round
    if startGame and not stateResult:
        initialTime = time.time()
        startGame = False
        timer = 0

    if not stateResult:
        timer = time.time() - initialTime
        cv2.putText(imgBG, str(int(timer)), (605, 435),
                    cv2.FONT_HERSHEY_PLAIN, 6, (255, 255, 255), 4)

    # Evaluate move after 3 seconds
    if timer > 3 and not stateResult:
        stateResult = True
        timer = 0

        if hands:
            playerMove = None
            hand = hands[0]
            fingers = detector.fingersUp(hand)

            if fingers == [0, 0, 0, 0, 0]:
                playerMove = 1
            elif fingers == [1, 1, 1, 1, 1]:
                playerMove = 2
            elif fingers == [0, 1, 1, 0, 0]:
                playerMove = 3
            elif fingers == [0, 1, 0, 0, 0]:
                playerMove = 4

            randomNumber = random.randint(1, 4)
            imgAI = cv2.imread(f'Resources/{randomNumber}.png', cv2.IMREAD_UNCHANGED)
            imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

            # Player Wins
            if (playerMove == 1 and randomNumber == 4) or \
               (playerMove == 2 and randomNumber == 1) or \
               (playerMove == 3 and randomNumber == 2) or \
               (playerMove == 4 and randomNumber == 3) or \
               (playerMove == 2 and randomNumber == 4):
                scores[1] += 1

            # AI Wins
            if (playerMove == 3 and randomNumber == 4) or \
               (playerMove == 1 and randomNumber == 2) or \
               (playerMove == 2 and randomNumber == 3) or \
               (playerMove == 4 and randomNumber == 1) or \
               (playerMove == 4 and randomNumber == 2):
                scores[0] += 1

            lastRoundTime = time.time()

    # Show webcam image
    imgBG[234:654, 795:1195] = imgScaled

    # Display AI move result
    if stateResult and imgAI is not None:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

        # After cooldown, prepare next round
        if (currentTime - lastRoundTime) > roundCooldown:
            stateResult = False
            startGame = True
            imgAI = None

    # Display scores
    cv2.putText(imgBG, str(scores[0]), (410, 215),
                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (1112, 215),
                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    # Show the game frame
    cv2.imshow("BG", imgBG)
    key = cv2.waitKey(1)

    # Allow exit with 'n' key
    if key == ord('n'):
        break

    # Check for winner
    if scores[0] == 5:
        print("AI wins", scores[0], "points")
        messagebox.showinfo("GAME OVER", "         AI WINS        ")
        break

    if scores[1] == 5:
        print("Player wins", scores[1], "points")
        messagebox.showinfo("GAME OVER", "       PLAYER WINS       ")
        break

cap.release()
cv2.destroyAllWindows()

import cv2 as cv2


def start():

    image = cv2.imread('C:\\Users\\tomas\\PycharmProjects\\terminal\\content\\images\\neferpitou_drawing.png', cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    s = int(w / 8)

    k = s
    print(k % 2)
    if k % 2 == 0: k += 1
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, k, 12.0)

    # Downsize image (by factor 4) to speed up morphological operations
    gray = cv2.resize(gray, dsize=(0, 0), fx=1, fy=1)
    cv2.imshow("Gray resized", gray)
    cv2.imwrite('Gray_resized.png', gray)

    # Morphological opening: Get rid of the stuff at the top of the ellipse
    gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50)))
    cv2.imshow("Gray removed noise", gray)
    cv2.imwrite('Gray_removed_noise.png', gray)

    # Resize image to original size
    gray = cv2.resize(gray, dsize=(image.shape[1], image.shape[0]))

    # Find contours
    cnts, hier = cv2.findContours(gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

    # Draw found contours in input image
    image = cv2.drawContours(image, cnts, -1, (0, 0, 255), 2)

    for i, cont in enumerate(cnts):
        try:
            h = hier[0, i, :]
            print(h)
            if h[3] != -1:
                elps = cv2.fitEllipse(cnts[i])
            elif h[2] == -1:
                elps = cv2.fitEllipse(cnts[i])
            print(elps)
            cv2.ellipse(image, elps, (0, 255, 0), 2)
        except cv2.error: pass

    # Downsize image
    out_image = cv2.resize(image, dsize=(0, 0), fx=0.25, fy=0.25)
    cv2.imshow("Output image", out_image)
    cv2.imwrite('drawing.png', out_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
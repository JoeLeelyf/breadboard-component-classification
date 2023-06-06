import numpy as np
import cv2
import os

"""
    The sort customs for breadboard detection
"""


def customSortX(contour):
    return (contour[0], contour[2])


def customSortY(contour):
    return (contour[2], contour[0])


"""
    detect and construct the coordinate of images
    return: list_x, list_y , picture of contours
"""


def detectImage(image_path):
    breadboard_image = cv2.imread(image_path)
    # preprocess
    gray_breadboard = cv2.cvtColor(breadboard_image, cv2.COLOR_BGR2GRAY)
    # binary
    _, binary_breadboard = cv2.threshold(
        gray_breadboard, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    )
    # find contours
    contours, _ = cv2.findContours(
        binary_breadboard, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # list of breadboard coordinates
    contour_coordinates = []

    # convert the image for drawing
    detect_contours_image = cv2.cvtColor(binary_breadboard, cv2.COLOR_GRAY2BGR)

    # filter the contours
    min_white_ratio_rectangle = 0.6
    min_white_ratio_circle = 0.4
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        # approximate the contour with 4 vertices
        approx = cv2.approxPolyDP(contour, 0.05 * perimeter, True)
        # filter the contours that are not rectangle
        # filter contours according to the area
        contour_area = cv2.contourArea(contour)
        if 100 < contour_area < 700:
            # get the rectangle contour
            x, y, w, h = cv2.boundingRect(contour)
            # get the circle contour
            (x_circle, y_circle), radius = cv2.minEnclosingCircle(contour)

            # check if the contour contains enough white pixels (rectangle)
            contour_area_rec = w * h
            white_area = cv2.countNonZero(binary_breadboard[y : y + h, x : x + w])
            if white_area / contour_area_rec < min_white_ratio_rectangle:
                continue

            # check if the contour contains enough white pixels (circle)
            contour_area_circle = np.pi * radius * radius
            white_area = cv2.countNonZero(
                binary_breadboard[
                    int(y_circle - radius) : int(y_circle + radius),
                    int(x_circle - radius) : int(x_circle + radius),
                ]
            )
            if white_area / contour_area_circle < min_white_ratio_circle:
                continue

            contour_coordinates.append((x, x + w, y, y + h))
            # draw the rectangle contour
            cv2.rectangle(detect_contours_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # sort the coordinate according to x and y
    sorted_coordinates = sorted(contour_coordinates, key=customSortX)

    # list of sequences of x coordinates
    list_x = []
    for coordinate in sorted_coordinates:
        if not len(list_x):
            list_x.append(coordinate)
        # threshold = 30 to distinguish different plugs
        elif coordinate[0] > list_x[len(list_x) - 1][0] + 30:
            list_x.append(coordinate)
        else:
            continue

    sorted_coordinates = sorted(contour_coordinates, key=customSortY)

    # list of sequences of y coordinates
    list_y = []
    for coordinate in sorted_coordinates:
        if not len(list_y):
            list_y.append(coordinate)
        elif coordinate[3] > list_y[len(list_y) - 1][3] + 30:
            list_y.append(coordinate)
        else:
            continue

    return list_x, list_y, detect_contours_image


"""
    query elements
    input: list_x, list_y and element_contours
    each contours consist of [name, x1, y1, x2, y2(rectangle)]
    output: return_list is a dict of elements positions

"""


def query_element(list_x, list_y, element_contours):
    return_list = []
    # reverse list_x and list_y
    reverse_list_x = list_x[::-1]
    reverse_list_y = list_y[::-1]
    for contour in element_contours:
        element_dict = {}
        name, x1, y1, x2, y2 = contour
        element_dict["name"] = name
        for index_left in range(len(list_x)):
            if list_x[index_left][0] > x1 or list_x[index_left][1] > x1:
                element_dict["index_left"] = index_left
                break
        for index_right in range(len(reverse_list_x)):
            if (
                reverse_list_x[index_right][0] < x2
                or reverse_list_x[index_right][1] < x2
            ):
                element_dict["index_right"] = len(reverse_list_x) - index_right - 1
                break
        for index_up in range(len(list_y)):
            if list_y[index_up][2] > y1 or list_y[index_up][3] > y1:
                element_dict["index_up"] = index_up
                break
        for index_down in range(len(reverse_list_y)):
            if reverse_list_y[index_down][2] < y2 or reverse_list_y[index_down][3] < y2:
                element_dict["index_down"] = len(reverse_list_y) - index_down - 1
                break

        return_list.append(element_dict)

        return return_list


if __name__ == "__main__":
    image_path = "./images/temp/test_1_breadboard.jpg"
    list_x, list_y, detect_image = detectImage(image_path)
    print(list_x)
    print(list_y)
    return_list = query_element(list_x, list_y, [["Resistor", 890, 1327, 1070, 1520]])
    print(return_list)
    cv2.imshow("detect_image", detect_image)
    cv2.waitKey(0)

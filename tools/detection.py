import numpy as np
import cv2
import os
from sklearn.cluster import KMeans

"""
    The sort customs for breadboard detection
"""


def customSortX(contour):
    return (contour[0], contour[2])


def customSortY(contour):
    return (contour[2], contour[0])


def customSortX2(contour):
    return contour[0]


def customSortY2(contour):
    return contour[1]


"""
    detect and construct the coordinate of images
    return: list_x, list_y , picture of contours
"""


def detect_image(image_path):
    breadboard_image = cv2.imread(image_path)
    # get image size
    height, width, _ = breadboard_image.shape
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

    contour_area = [[], [], [], [], [], [], []]
    height_dividend = height / 20
    height_dividend_list = [
        height_dividend * 1.5,
        height_dividend * 5,
        height_dividend * 9,
        height_dividend * 11,
        height_dividend * 15,
        height_dividend * 18.5,
    ]
    # divide the breadboard into 7 parts according to the height
    for coordinate in sorted_coordinates:
        x1, x2, y1, y2 = coordinate
        contour = [int((x1 + x2) / 2), int((y1 + y2) / 2)]
        # divide the breadboard into 7 parts according to the height
        if y1 < height_dividend_list[0]:
            contour_area[0].append(contour)
        elif y1 < height_dividend_list[1]:
            contour_area[1].append(contour)
        elif y1 < height_dividend_list[2]:
            contour_area[2].append(contour)
        elif y1 < height_dividend_list[3]:
            contour_area[3].append(contour)
        elif y1 < height_dividend_list[4]:
            contour_area[4].append(contour)
        elif y1 < height_dividend_list[5]:
            contour_area[5].append(contour)
        else:
            contour_area[6].append(contour)

    # sort each area
    for i in range(len(contour_area)):
        if i == 0 or i == 3 or i == 6:
            contour_area[i] = sorted(contour_area[i], key=customSortY2)
        else:
            contour_area[i] = sorted(contour_area[i], key=customSortX2)

    # divide the dot into different parts according to the voltage
    voltage_area_horizontal = [[], [], [], [], [], []]
    voltage_area_vertical = [[], [], [], []]
    for i in range(len(contour_area)):
        if i == 0 or i == 3 or i == 6:
            # get mean y index of the first five dot
            y_mean = int(
                (
                    contour_area[i][0][1]
                    + contour_area[i][1][1]
                    + contour_area[i][2][1]
                    + contour_area[i][3][1]
                    + contour_area[i][4][1]
                ) / 5
            )
            # divide dot into 6 parts according to y index
            for contour in contour_area[i]:
                if abs(contour[1] - y_mean) < 40:
                    voltage_area_horizontal[2 * i // 3 + 0].append(contour)
                else:
                    voltage_area_horizontal[2 * i // 3 + 1].append(contour)
        else:
            vertical_index = 0
            if i == 1 or i == 2:
                vertical_index = i - 1
            elif i == 4 or i == 5:
                vertical_index = i - 2
            change_colomn_flag = True
            colomn = []
            for j in range(len(contour_area[i])):
                contour = contour_area[i][j]
                if change_colomn_flag:
                    colomn_x = contour[0]
                    colomn.append(contour)
                    if (
                        abs(
                            contour_area[i][min(len(contour_area[i]) - 1, j + 1)][0]
                            - colomn_x
                        )
                        > 5
                    ):
                        voltage_area_vertical[vertical_index].append(colomn)
                        colomn = []
                        continue
                    change_colomn_flag = False
                else:
                    if abs(contour[0] - colomn_x) <= 5:
                        colomn.append(contour)
                    else:
                        voltage_area_vertical[vertical_index].append(colomn)
                        colomn = []
                        colomn_x = contour[0]
                        colomn.append(contour)
                        change_colomn_flag = True
    # draw rectangle of each contour area
    # get the y index bounds of each area
    
    y_index_bounds = []
    bounding_bias = 60
    for i in range(len(contour_area)):
        x_1_min = min(contour_area[i], key=lambda x: x[0])[0] - bounding_bias
        x_1_max = max(contour_area[i], key=lambda x: x[0])[0] + bounding_bias
        y_1_min = min(contour_area[i], key=lambda x: x[1])[1] - bounding_bias
        y_1_max = max(contour_area[i], key=lambda x: x[1])[1] + bounding_bias
        y_index_bounds.append([y_1_min, y_1_max])
        cv2.rectangle(
            detect_contours_image,
            (x_1_min - 10, y_1_min - 10),
            (x_1_max + 10, y_1_max + 10),
            (0, 200, 200),
            4,
        )

    # draw rectangle for each vlotage area
    for area in voltage_area_horizontal:
        x_min = min([coordinate[0] for coordinate in area])
        x_max = max([coordinate[0] for coordinate in area])
        y_min = min([coordinate[1] for coordinate in area])
        y_max = max([coordinate[1] for coordinate in area])
        cv2.rectangle(
            detect_contours_image, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2
        )
    for i in range(len(voltage_area_vertical)):
        for area in voltage_area_vertical[i]:
            x_min = min([coordinate[0] for coordinate in area])
            x_max = max([coordinate[0] for coordinate in area])
            y_min = min([coordinate[1] for coordinate in area])
            y_max = max([coordinate[1] for coordinate in area])
            cv2.rectangle(
                detect_contours_image,
                (x_min - 2, y_min - 2),
                (x_max + 2, y_max + 2),
                (0, 0, 255),
                4,
            )

    # replace the exact coodinate with mean value
    for i in range(len(voltage_area_horizontal)):
        y_mean = int(
            sum([coordinate[1] for coordinate in voltage_area_horizontal[i]])
            / len(voltage_area_horizontal[i])
        )
        voltage_area_horizontal[i] = y_mean
    voltage_area_horizontal_1 = voltage_area_horizontal[:2]
    voltage_area_horizontal_2 = voltage_area_horizontal[2:4]
    voltage_area_horizontal_3 = voltage_area_horizontal[4:]
    voltage_area_horizontal = [
        voltage_area_horizontal_1,
        voltage_area_horizontal_2,
        voltage_area_horizontal_3,
    ]
    for i in range(len(voltage_area_vertical)):
        for j in range(len(voltage_area_vertical[i])):
            x_mean = int(
                sum([coordinate[0] for coordinate in voltage_area_vertical[i][j]])
                / len(voltage_area_vertical[i][j])
            )
            voltage_area_vertical[i][j] = x_mean

    return (
        y_index_bounds,
        voltage_area_horizontal,
        voltage_area_vertical,
        detect_contours_image,
    )


"""
    query_component
"""


def query_component(image_path, componet_list):
    componet_info = []
    (
        y_index_bounds,
        voltage_area_horizontal,
        voltage_area_vertical,
        Image,
    ) = detect_image(image_path)
    # draw rectangle of each componet
    for componet in componet_list:
        cv2.rectangle(
            Image,
            (componet[1], componet[2]),
            (componet[3], componet[4]),
            (255, 0, 255),
            2,
        )

    # get upper and lower index of bounding box
    for i in range(len(componet_list)):
        name, x_1, y_1, x_2, y_2 = (
            componet_list[i][0],
            componet_list[i][1],
            componet_list[i][2],
            componet_list[i][3],
            componet_list[i][4],
        )
        componet = []
        # get name and x index of bounding box
        componet.append(name)
        componet.append(x_1)
        componet.append(x_2)
        componet.append(y_1)
        componet.append(y_2)
        lower_index = 0
        upper_index = 0
        # get y index of bounding box
        for j in range(len(y_index_bounds)):
            if y_1 >= y_index_bounds[j][0] and y_1 <= y_index_bounds[j][1]:
                lower_index = j
            if y_2 >= y_index_bounds[j][0] and y_2 <= y_index_bounds[j][1]:
                upper_index = j
        componet.append(lower_index)
        componet.append(upper_index)
        componet_info.append(componet)

    return_list = []
    # get voltage of each componet's two end
    vertical_bias = 40
    horizantal_bias = 40
    len_v = 0
    for i in range(len(voltage_area_vertical)):
        len_v += len(voltage_area_vertical[i])
    for componet in componet_info:
        return_componet = {}
        name, x_1, x_2, y_1, y_2, lower_index, upper_index = (
            componet[0],
            componet[1],
            componet[2],
            componet[3],
            componet[4],
            componet[5],
            componet[6],
        )
        return_componet["name"] = name
        return_componet["voltage_1"] = -1
        return_componet["voltage_2"] = -1
        # when the two end of componet are in the same area
        if lower_index == upper_index:
            if lower_index == 0 or lower_index == 3 or lower_index == 6:
                raise Exception("Componet is cross between the voltage")

            elif lower_index == 1:
                for index in range(len(voltage_area_vertical[0])):
                    if abs(x_1 - voltage_area_vertical[0][index]) < vertical_bias:
                        return_componet["voltage_1"] = index
                    if abs(x_2 - voltage_area_vertical[0][index]) < vertical_bias:
                        return_componet["voltage_2"] = index

            elif lower_index == 2:
                for index in range(len(voltage_area_vertical[1])):
                    if abs(x_1 - voltage_area_vertical[1][index]) < vertical_bias:
                        return_componet["voltage_1"] = index + len(
                            voltage_area_vertical[0]
                        )
                    if abs(x_2 - voltage_area_vertical[1][index]) < vertical_bias:
                        return_componet["voltage_2"] = index + len(
                            voltage_area_vertical[0]
                        )
            elif lower_index == 4:
                for index in range(len(voltage_area_vertical[2])):
                    if abs(x_1 - voltage_area_vertical[2][index]) < vertical_bias:
                        return_componet["voltage_1"] = (
                            index
                            + len(voltage_area_vertical[0])
                            + len(voltage_area_vertical[1])
                        )
                    if abs(x_2 - voltage_area_vertical[2][index]) < vertical_bias:
                        return_componet["voltage_2"] = (
                            index
                            + len(voltage_area_vertical[0])
                            + len(voltage_area_vertical[1])
                        )
            elif lower_index == 5:
                for index in range(len(voltage_area_vertical[3])):
                    if abs(x_1 - voltage_area_vertical[3][index]) < vertical_bias:
                        return_componet["voltage_1"] = (
                            index
                            + len(voltage_area_vertical[0])
                            + len(voltage_area_vertical[1])
                            + len(voltage_area_vertical[2])
                        )
                    if abs(x_2 - voltage_area_vertical[3][index]) < vertical_bias:
                        return_componet["voltage_2"] = (
                            index
                            + len(voltage_area_vertical[0])
                            + len(voltage_area_vertical[1])
                            + len(voltage_area_vertical[2])
                        )
        # when the two end of componet are in the different area
        else:
            mean_x = (x_1 + x_2) / 2
            if lower_index == 0:
                if upper_index == 1:
                    for index in range(len(voltage_area_vertical[0])):
                        if (
                            abs(mean_x - voltage_area_vertical[0][index])
                            < vertical_bias
                        ):
                            return_componet["voltage_1"] = index
                    for index in range(len(voltage_area_horizontal[0])):
                        if (
                            abs(y_2 - voltage_area_horizontal[0][index])
                            < horizantal_bias
                        ):
                            return_componet["voltage_2"] = index + len_v
            elif lower_index == 1:
                if upper_index == 2:
                    for index in range(len(voltage_area_vertical[1])):
                        if (
                            abs(mean_x - voltage_area_vertical[1][index])
                            < vertical_bias
                        ):
                            return_componet["voltage_1"] = index + len(
                                voltage_area_vertical[0]
                            )
                    for index in range(len(voltage_area_vertical[0])):
                        if (
                            abs(mean_x - voltage_area_vertical[0][index])
                            < vertical_bias
                        ):
                            return_componet["voltage_2"] = index
            elif lower_index == 2:
                if upper_index == 3:
                    for index in range(len(voltage_area_vertical[2])):
                        if (
                            abs(mean_x - voltage_area_vertical[2][index])
                            < vertical_bias
                        ):
                            return_componet["voltage_1"] = index + len(
                                voltage_area_vertical[0]
                            )
                    for index in range(len(voltage_area_horizontal[1])):
                        if (
                            abs(y_2 - voltage_area_horizontal[1][index])
                            < horizantal_bias
                        ):
                            return_componet["voltage_2"] = index + 2 + len_v
            elif lower_index == 3:
                if upper_index == 4:
                    for index in range(len(voltage_area_vertical[3])):
                        if (
                            abs(mean_x - voltage_area_vertical[3][index])
                            < vertical_bias
                        ):
                            return_componet["voltage_1"] = (
                                index
                                + len(voltage_area_vertical[0])
                                + len(voltage_area_vertical[1])
                            )
                    for index in range(len(voltage_area_horizontal[2])):
                        if (
                            abs(y_1 - voltage_area_horizontal[2][index])
                            < horizantal_bias
                        ):
                            return_componet["voltage_2"] = index + 3 + len_v
            elif lower_index == 4:
                if upper_index == 5:
                    for index in range(len(voltage_area_vertical[2])):
                        if (
                            abs(mean_x - voltage_area_vertical[2][index])
                            < vertical_bias
                        ):
                            return_componet["voltage_1"] = (
                                index
                                + len(voltage_area_vertical[0])
                                + len(voltage_area_vertical[1])
                            )
                    for index in range(len(voltage_area_vertical[3])):
                        if (
                            abs(mean_x - voltage_area_vertical[3][index])
                            < vertical_bias
                        ):
                            return_componet["voltage_2"] = (
                                index
                                + len(voltage_area_vertical[0])
                                + len(voltage_area_vertical[1])
                                + len(voltage_area_vertical[2])
                            )
            elif lower_index == 5:
                if upper_index == 6:
                    for index in range(len(voltage_area_vertical[3])):
                        if (
                            abs(mean_x - voltage_area_vertical[3][index])
                            < vertical_bias
                        ):
                            return_componet["voltage_1"] = (
                                index
                                + len(voltage_area_vertical[0])
                                + len(voltage_area_vertical[1])
                                + len(voltage_area_vertical[2])
                            )
                    for index in range(len(voltage_area_horizontal[3])):
                        if (
                            abs(y_2 - voltage_area_horizontal[3][index])
                            < horizantal_bias
                        ):
                            return_componet["voltage_2"] = index + 4 + len_v
        if return_componet["voltage_1"] == -1 or return_componet["voltage_2"] == -1:
            pass
        else:
            return_list.append(return_componet)

    return_list = Transfer(return_list)
    return return_list


"""
    Transfer
"""


def Transfer(list1):
    list1 = sorted(list1, key=lambda x: x['voltage_1'])
    for ele in list1:
        if ele['name'] == 'Wire':
            temp1 = ele['voltage_1']
            temp2 = ele['voltage_2']
            list1.remove(ele)
            for elee in list1:
                if elee['voltage_2'] == temp2:
                    elee['voltage_2'] = temp1
    list2 = set()
    for i in list1:
        list2.add(i['voltage_1'])
        list2.add(i['voltage_2'])
    list2 = list(list2)
    list2.sort()
    list3 = {}
    for i in range(len(list2)):
        list3[list2[i]] = i
    list4 = []
    for i in list1:
        i['voltage_1'] = list3[i['voltage_1']]
        i['voltage_2'] = list3[i['voltage_2']]
        list4.append((i['name'], i['voltage_1'], i['voltage_2']))


if __name__ == "__main__":
    image_path = "./images/temp/test_1_breadboard.jpg"
    detect_image(image_path)
    query_component(image_path, [['Resistor', 2190, 926, 2265, 1169], ['Resistor', 1520, 505, 1589, 759], ['Resistor', 1767, 344, 2036, 426], ['Resistor', 1551, 237, 1797, 317], ['Resistor', 1541, 878, 1812, 946], ['Resistor', 1765, 774, 2034, 842], ['Wire', 1977, 465, 2045, 715]])

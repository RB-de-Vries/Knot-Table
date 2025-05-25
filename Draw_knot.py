import pygame
from math import floor, radians
from copy import deepcopy
import numpy
import ast

from Data_edges import apply_R3

# BUG: A knot where R1 can be applied may not resolve the frame, causing infinite drawing.

# knot_list = []
# file = open(f"10.pass_reduced/{8}.txt", "r")
# for line in file:
#     knot = ast.literal_eval(line)
#     knot_list.append(knot)
    

knot_list = [
    [[1, 5, 2, 4], [3, 11, 4, 10], [5, 13, 6, 12], [7, 1, 8, 14], [9, 3, 10, 2], [11, 9, 12, 8], [13, 7, 14, 6]],
[[1, 5, 2, 4], [3, 11, 4, 10], [5, 1, 6, 14], [7, 13, 8, 12], [9, 3, 10, 2], [11, 7, 12, 6], [13, 9, 14, 8]]
    ]

# pygame setup
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
knot_number = 0

# Text properties
text_color = "black"
font = pygame.font.Font(None, 36)

margin_left = 25
spacing = 75


def draw_semicircle(p1, p2, direction, gap = "no"): # direction = "left" or "right"
    x1, y1 = p1
    _, y2 = p2
    mid_y = (y1 + y2) / 2
    radius = abs(y2 - y1) / 2
    rect = pygame.Rect(x1 - radius, mid_y - radius, radius*2, radius*2)
    start_angle = radians(90)
    end_angle = radians(270)
    if direction == "right":
        start_angle, end_angle = end_angle, start_angle
    if gap == "no":
        pygame.draw.arc(screen, "black", rect, start_angle, end_angle, 4)
    else:
        gap_size = radians(8)
        pygame.draw.arc(screen, "black", rect, start_angle, gap - gap_size, 4)
        pygame.draw.arc(screen, "black", rect, gap + gap_size, end_angle, 4)

def draw_ellips(p1, p2, direction, gap = "no"):
    x1, y1 = p1
    _, y2 = p2
    mid_y = (y1 + y2) / 2
    radius = abs(y2 - y1) / 2
    rect = pygame.Rect(x1 - (radius/2), mid_y - radius, radius, radius*2)
    start_angle = radians(90)
    end_angle = radians(270)
    if direction == "right":
        start_angle, end_angle = end_angle, start_angle
    if gap == "no":
        pygame.draw.arc(screen, "black", rect, start_angle, end_angle, 4)
    else:
        gap_size = radians(8)
        pygame.draw.arc(screen, "black", rect, start_angle, gap - gap_size, 4)
        pygame.draw.arc(screen, "black", rect, gap + gap_size, end_angle, 4)

def draw_0_4(p1, p2, p3, p4, sign): #
    draw_semicircle(p1, p3, "left", gap = radians(150))
    draw_semicircle(p2, p4, "left")

def draw_cross(p1, p2, p3, p4):
    middle = tuple(numpy.divide(numpy.add(p1, p3),(2,2)))
    gapsize = tuple(numpy.divide(numpy.subtract(p3, p1), (10,10)))
    pygame.draw.line(screen, "black", p1, tuple(numpy.subtract(middle, gapsize)), 4)
    pygame.draw.line(screen, "black", tuple(numpy.add(middle, gapsize)), p3, 4)
    pygame.draw.line(screen, "black", p2, p4, 4)

def draw_fork(p1,p2,p3,p4, gap):
    if gap == "line":
        middle = tuple(numpy.divide(numpy.add(p1, p3),(2,2)))
        gapsize = tuple(numpy.divide(numpy.subtract(p3, p1), (10,10)))
        # pygame.draw.line(screen, "black", p1, tuple(numpy.subtract(middle, gapsize)), 4)
        pygame.draw.line(screen, "black", p1, tuple(numpy.subtract(middle, gapsize)), 4)
        pygame.draw.line(screen, "black", tuple(numpy.add(middle, gapsize)), p3, 4)
        draw_ellips(p2,p4, "left")
    else:
        pygame.draw.line(screen, "black", p1, p3, 4)
        draw_ellips(p2,p4, "left", radians(180))

def update_point_list(len_front, front_number):
    startheight = 0
    if len_front%2: # odd
        startheight = HEIGHT/2 + floor(len_front/2)*spacing
    else: # even
        startheight = HEIGHT/2 + (len_front-1)*(spacing/2)
    points = [(margin_left+ spacing*front_number, startheight - i*spacing) for i in range(len_front)]
    return points

def draw_knot(knot):
    current_crossing = knot[0]
    front = current_crossing
    len_front = len(front)
    knot.remove(current_crossing)
    
    front_number = 1
    points = update_point_list(len(front), front_number)

    draw_0_4(points[0], points[1], points[2], points[3], "+")
    for idx, point in enumerate(points):
            text_surface = font.render(str(front[idx]), True, "black")
            screen.blit(text_surface, (point[0] - 10, point[1] - 30))
    
    next_front = front
    next_points = points
    while len(front) != 0:
        # print(front)

        draw_list = []
        skip_next = False
        front_number += 1
        points = next_points
        front = next_front
        len_front = len(front)

        # create front and lists what to draw
        for i in range(len_front):
            if skip_next:
                skip_next = False
                continue
            
            if i < len(front) - 1:
                if front[i] == front[i+1]:
                    # semi
                    # next_points = update_point_list(len(next_front), front_number)
                    draw_list.append("cap")
                    #draw_semicircle(points[i], points[i+1], "right")
                    skip_next = True
                    next_front.pop(i)
                    next_front.pop(i)
                    continue

                if len(knot) == 0:   
                    # next_points = update_point_list(len(next_front), front_number)
                    # draw a line
                    draw_list.append("line")
                    # pygame.draw.line(screen,"black", points[i], next_points[i+front_offset], 4)
                    continue
                
                found = False
                for crossing in knot:
                    # find other half edge
                    if front[i] in crossing:
                        # bi-gon/cross
                        found = True
                
                        if front[i+1] in crossing:
                            # update front
                            #print(front)

                            idx_i = crossing.index(front[i])
                            idx_i2 = crossing.index(front[i+1])
                            if idx_i +1 != idx_i2:
                                next_front[i] = crossing[(idx_i+1)%4]
                                next_front[i+1] = crossing[(idx_i2-1)%4]
                            else:
                                next_front[i] = crossing[(idx_i-1)%4]
                                next_front[i+1] = crossing[(idx_i2+1)%4]
                            #print(front)

                            # next_points = update_point_list(len(next_front), front_number)

                            # make a cross
                            if crossing[0] == next_front[i] or crossing[2] == next_front[i]:
                                draw_list.append("cross_under")
                            else:
                                draw_list.append("cross_over")
                            # draw_cross(points[i], points[i+1], next_points[i+1], next_points[i])
                            skip_next = True
                            knot.remove(crossing)
                            break
                        else:
                            # next_points = update_point_list(len(next_front), front_number)
                            # draw a line
                            # pygame.draw.line(screen,"black", points[i], next_points[i], 4)
                            draw_list.append("line")
                            break
                if not found:
                    draw_list.append("line")
                    continue

            else:
                # next_points = update_point_list(len(next_front), front_number)
                # draw a line
                draw_list.append("line")
                # pygame.draw.line(screen,"black", points[i], next_points[i+front_offset], 4)
        
        if len(set(draw_list)) == 1 and draw_list[0] == "line":
            done = False
            for i in range(len(front)):
                if done:
                    done = False
                    break
                for crossing in knot:
                    if front[i] in crossing:
                    # find other half edge
                        idx = crossing.index(front[i])
                        next_front.pop(i)
                        next_front.insert(i, crossing[(idx - 1)%4])
                        next_front.insert(i, crossing[(idx - 2)%4])
                        next_front.insert(i, crossing[(idx - 3)%4])
                        knot.remove(crossing)
                        if crossing[0] == next_front[i] or crossing[2] == next_front[i]:
                            draw_list[i] = "fork_semi"
                        else:
                            draw_list[i] = "fork_line"
                        done = True
                        break


        # draw front labels
        next_points = update_point_list(len(next_front), front_number)
        for idx, point in enumerate(next_points):
            text_surface = font.render(str(next_front[idx]), True, "black")
            screen.blit(text_surface, (point[0] - 10, point[1] - 30))

        # draw from list
        i = 0
        front_offset = 0
        for operation in draw_list:
            if operation == "line":
                pygame.draw.line(screen,"black", points[i], next_points[i+front_offset], 4)
                i+=1
            elif operation == "cross_over":
                draw_cross(points[i], points[i+1], next_points[i+1], next_points[i + front_offset])
                i+=2
            elif operation == "cross_under":
                draw_cross(next_points[i + front_offset], points[i], points[i+1], next_points[i+1])
                i+=2
            elif operation == "cap":
                draw_semicircle(points[i], points[i+1], "right")
                front_offset -= 2
                i+=2
            elif operation == "fork_line":
                draw_fork(points[i], next_points[i],next_points[i+1], next_points[i+2], "line")
                front_offset += 2
                i+= 1
            elif operation == "fork_semi":
                draw_fork(points[i], next_points[i],next_points[i+1], next_points[i+2], "semi")
                front_offset += 2
                i+= 1
    

                    









while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                knot_number = (knot_number - 1)%len(knot_list)
            elif event.key == pygame.K_RIGHT:
                knot_number = (knot_number + 1)%len(knot_list)
    
    screen.fill("white")

    # Draw images with numbers    
    title_text = {"x": 0, "y": 0, "text": f"{knot_number + 1}, {knot_list[knot_number]}"}
    text_surface = font.render(title_text["text"], True, text_color)
    screen.blit(text_surface, (title_text["x"], title_text["y"]))

    draw_knot(deepcopy(knot_list[knot_number]))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()


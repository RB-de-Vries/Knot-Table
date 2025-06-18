import pygame
from math import floor, radians
from copy import deepcopy
import numpy
import ast

from Data_edges import mix_reduced_dict_load

knot_list = []

# i = 10
# file = open(f"8.pass_reduced/{i}.txt", "r")
# for line in file:
#     knot = ast.literal_eval(line)
#     knot_list.append(knot)

i = 10
knot_dict = mix_reduced_dict_load(i)
for _, value in knot_dict.items():
    knot_list.append(value[0])

show_numbers = True

pos, size = (0,0)
max_front_number = 0
max_front_size = 0

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

# Knot --> image
def Capture(display,name,pos,size): # (pygame Surface, String, tuple, tuple)
    image = pygame.Surface(size)  # Create image surface
    image.blit(display,(0,0),(pos,size))  # Blit portion of the display to the image
    pygame.image.save(image,name)  # Save the image to the disk

# Draw a semi-circle (with gap)
def draw_semicircle(p1, p2, direction, gap = "no"):
    # unpack Coordinates
    x1, y1 = p1
    _, y2 = p2
    # Find midpoint and radius
    mid_y = (y1 + y2) / 2
    radius = abs(y2 - y1) / 2
    rect = pygame.Rect(x1 - radius, mid_y - radius, radius*2, radius*2)
    start_angle = radians(90)
    end_angle = radians(270)
    # Switch the start and endpoint if we want the semicircle on the right side
    if direction == "right":
        start_angle, end_angle = end_angle, start_angle
    # Place a gap given an angle if needed
    if gap == "no":
        pygame.draw.arc(screen, "black", rect, start_angle, end_angle, 4)
    else:
        gap_size = radians(8)
        pygame.draw.arc(screen, "black", rect, start_angle, gap - gap_size, 4)
        pygame.draw.arc(screen, "black", rect, gap + gap_size, end_angle, 4)

# Draw an ellipse (with gap)
def draw_ellips(p1, p2, direction, gap = "no"):
    # unpack Coordinates
    x1, y1 = p1
    _, y2 = p2
    # Find midpoint and radius
    mid_y = (y1 + y2) / 2
    radius = abs(y2 - y1) / 2
    rect = pygame.Rect(x1 - (radius/2), mid_y - radius, radius, radius*2)
    start_angle = radians(90)
    end_angle = radians(270)
    # Switch the start and endpoint if we want the semicircle on the right side
    if direction == "right":
        start_angle, end_angle = end_angle, start_angle
    # Place a gap given an angle if needed
    if gap == "no":
        pygame.draw.arc(screen, "black", rect, start_angle, end_angle, 4)
    else:
        gap_size = radians(8)
        pygame.draw.arc(screen, "black", rect, start_angle, gap - gap_size, 4)
        pygame.draw.arc(screen, "black", rect, gap + gap_size, end_angle, 4)

# Draws the starting piece
def draw_0_4(p1, p2, p3, p4, sign):
    draw_semicircle(p1, p3, "left", gap = radians(150))
    draw_semicircle(p2, p4, "left")

# Draws a cross
def draw_cross(p1, p2, p3, p4):
    middle = tuple(numpy.divide(numpy.add(p1, p3),(2,2)))
    gapsize = tuple(numpy.divide(numpy.subtract(p3, p1), (10,10)))
    pygame.draw.line(screen, "black", p1, tuple(numpy.subtract(middle, gapsize)), 4)
    pygame.draw.line(screen, "black", tuple(numpy.add(middle, gapsize)), p3, 4)
    pygame.draw.line(screen, "black", p2, p4, 4)

# Draws a fork
def draw_fork(p1,p2,p3,p4, gap):
    # The gap can eiher be part of the line or the ellipse
    if gap == "line":
        middle = tuple(numpy.divide(numpy.add(p1, p3),(2,2)))
        gapsize = tuple(numpy.divide(numpy.subtract(p3, p1), (10,10)))
        pygame.draw.line(screen, "black", p1, tuple(numpy.subtract(middle, gapsize)), 4)
        pygame.draw.line(screen, "black", tuple(numpy.add(middle, gapsize)), p3, 4)
        draw_ellips(p2,p4, "left")
    else:
        pygame.draw.line(screen, "black", p1, p3, 4)
        draw_ellips(p2,p4, "left", radians(180))

# Front --> screen Coordinates
def update_point_list(len_front, front_number):
    startheight = 0
    if len_front%2: # odd
        startheight = HEIGHT/2 + floor(len_front/2)*spacing
    else: # even
        startheight = HEIGHT/2 + (len_front-1)*(spacing/2)
    points = [(margin_left+ spacing*front_number, startheight - i*spacing) for i in range(len_front)]
    return points

# Draws the knot
def draw_knot(knot):
    current_crossing = knot[0]
    front = current_crossing
    len_front = len(front)
    knot.remove(current_crossing)
    
    front_number = 1
    points = update_point_list(len(front), front_number)

    draw_0_4(points[0], points[1], points[2], points[3], "+")
    if show_numbers:
        for idx, point in enumerate(points):
                text_surface = font.render(str(front[idx]), True, "black")
                screen.blit(text_surface, (point[0] - 10, point[1] - 30))
    
    next_front = front
    next_points = points
    while len(front) != 0:
        draw_list = []
        skip_next = False
        front_number += 1
        points = next_points
        front = next_front
        len_front = len(front)
        global max_front_size, max_front_number
        if len_front > max_front_size:
            max_front_size = len_front
        if front_number > max_front_number:
            max_front_number = front_number

        # create front and lists what to draw
        for i in range(len_front):
            if skip_next:
                skip_next = False
                continue
            
            if i < len(front) - 1:
                # can we place a cap?
                if front[i] == front[i+1]:
                    
                    draw_list.append("cap")
                    skip_next = True
                    next_front.pop(i)
                    next_front.pop(i)
                    continue
                
                # If there are no crossings left to place, we can only place a cap or a line
                if len(knot) == 0:   
                    draw_list.append("line")
                    continue
                
                found = False
                for crossing in knot:
                    # find other half edge
                    if front[i] in crossing:
                        # place the cross
                        found = True
                        if front[i+1] in crossing:
                            idx_i = crossing.index(front[i])
                            idx_i2 = crossing.index(front[i+1])
                            if idx_i +1 != idx_i2:
                                next_front[i] = crossing[(idx_i+1)%4]
                                next_front[i+1] = crossing[(idx_i2-1)%4]
                            else:
                                next_front[i] = crossing[(idx_i-1)%4]
                                next_front[i+1] = crossing[(idx_i2+1)%4]
                        
                            if crossing[0] == next_front[i] or crossing[2] == next_front[i]:
                                draw_list.append("cross_under")
                            else:
                                draw_list.append("cross_over")
    
                            skip_next = True
                            knot.remove(crossing)
                            break
                        # if a crossing can be placed, but not a cross
                        else:
                            draw_list.append("line")
                            break
                # if no crossings can be placed
                if not found:
                    draw_list.append("line")
                    continue
            # At the end of the front, only a line can be drawn
            else:
                draw_list.append("line")
                
        # If we can only draw lines with the rules above, we need to place a fork
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
        if show_numbers:
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
                max_front_number = 0
                max_front_size = 0
            elif event.key == pygame.K_RIGHT:
                knot_number = (knot_number + 1)%len(knot_list)
                max_front_number = 0
                max_front_size = 0
            elif event.key == pygame.K_p:
                pos = (0, HEIGHT/2 - floor(max_front_size/2)*spacing + 10)
                size = (margin_left+ spacing*max_front_number - 15,max_front_size*spacing - 25)
                Capture(screen,f"Knot_figures/{i}/{i}_{knot_number + 1}.png",pos,size)

    
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


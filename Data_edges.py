import re
import ast
import copy
from sympy import expand
from symengine import symbols, Rational, eye
from math import pi, e
import random

A, t = symbols("A t")
t1, t2 = symbols("t1 t2")

import time
from contextlib import contextmanager

@contextmanager
def timer(name="Code block"):
    start = time.time()
    yield
    end = time.time()
    print(f"[{name}] Elapsed time: {end - start:.6f} seconds")


# Reads Plantri output, returns the data as proper nested lists
def Read_Plantri_Data(s: str) -> list[list[int]]:
    pattern = re.findall(r'(\d+)\[(.*?)\]', s)
    result = []
    
    for key, values in pattern:
        # Convert space-separated numbers to a list of integers
        numbers = list(map(int, values.split()))  
        result.append([int(key), numbers])
    
    return result

# Knot in plantri-forman --> Gauss-like code 
def get_gauss(knot: list[list[int]]):
    # Start point
    gauss = [[1, 0]]

    
    crossing = knot[0][1]
    if crossing.count(crossing[0]) == 1:
        gauss.append([crossing[0], 1])
    else:
        if crossing[1] == crossing[0]:
            gauss.append([crossing[0], "-"])
        else:
            gauss.append([crossing[0], "+"])

    done = False
    while not done:
        next_crossing = knot[gauss[-1][0] - 1][1] # -1 because 0-indexing
        index = next_crossing.index(gauss[-2][0])
        if next_crossing.count(gauss[-2][0]) != 1:
            if gauss[-1][1] == "-":
                if next_crossing[index] == next_crossing[index + 1]:
                    index += 1
            else:
                if next_crossing[index] != next_crossing[index + 1]:
                    index = 3


        if next_crossing.count(next_crossing[(index + 2) % 4]) == 1:
            gauss.append([next_crossing[(index + 2) % 4], gauss[-1][0]])
        else:
            if next_crossing[(index + 2) % 4] == next_crossing[(index + 3) % 4]:
                gauss.append([next_crossing[(index + 2) % 4], "-"])
            else:
                gauss.append([next_crossing[(index + 2) % 4], "+"])

        # If we are back where we started, we made a full loop
        if gauss[-1] == gauss[1]:
            done = True
            gauss[0] = gauss[-2]
            return gauss

# 1.Plantri_Data --> 2.Plantri_knots   
def print_knots():
    for i in range(3,12):
        count = 0
        file = open(f"1.Plantri_Data/{i}.txt", "r")
        new_file = open(f"2.Plantri_knots/{i}.txt", "w")
        for line in file:
            knot = Read_Plantri_Data(line.rstrip()[3:])
            gauss_code = get_gauss(knot)
            if len(gauss_code) == ((len(knot)*2) + 2):
                new_file.write(f"{knot}\n")
                count += 1
                # print(knot)

# 2.Plantri_knots --> 3.Plantri_knots_with_sign
# Adds a sign to each crossing (all combinations)
def add_sign_to_crossing():
    def print_binary_sequences(n, knot):
        if n < 0:
            # print(knot)
            new_file.write(f"{knot}\n")
        else:
            knot_1 = copy.deepcopy(knot)
            knot_1[n].append("+")
            print_binary_sequences(n - 1, knot_1)
            knot_2 = copy.deepcopy(knot)
            knot_2[n].append("-")
            print_binary_sequences(n - 1, knot_2)
    for i in range(3,12):
        file = open(f"2.Plantri_knots/{i}.txt", "r")
        new_file = open(f"3.Plantri_knots_with_sign/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            # print(knot)
            print_binary_sequences(i-1, knot)
        file.close()
        new_file.close()

# Returns a list following the knot listing if the crossing goes over or under
def over_under_list(knot):
    ou_list = []
    seen = []
    gauss = get_gauss(knot)
    for i in range(0,len(gauss) - 2):
        if gauss[i][0] in seen:
            crossing = knot[gauss[i][0] - 1][1]
            sign = knot[gauss[i][0]-1][2]
            id_first = -1
            id_second = -1
            last_j = -1
            for j in range(len(gauss) - 2):
                if gauss[j][0] == gauss[i][0]:
                    if isinstance(gauss[j+1][1], str):
                        if gauss[j+1][1] == "+":
                            id_first = crossing.index(gauss[j+1][0])
                            if id_first != 0:
                                id_first += 1
                            last_j = j
                            break
                        else:
                            id_first = crossing.index(gauss[j+1][0])
                            if id_first == 0:
                                if crossing[1] != gauss[j+1][0]:
                                    id_first = 3
                            last_j = j
                            break
                    else:
                        id_first = crossing.index(gauss[j+1][0])
                        last_j = j
                        break
            if isinstance(gauss[i+1][1],str):
                if gauss[i+1][1] == "+":
                    id_second = crossing.index(gauss[i+1][0])
                    if id_second != 0:
                        id_second += 1
                else:
                    id_second = crossing.index(gauss[i+1][0])
                    if id_second == 0:
                        if crossing[1] != gauss[i+1][0]:
                                id_second = 3
            else:
                id_second = crossing.index(gauss[i+1][0])
        
            if id_first == ((id_second + 1)%4):
                if sign == "+":
                    ou_list[last_j] = [gauss[i][0],"over"]
                    ou_list.append([gauss[i][0],"under"])
                else:
                    ou_list[last_j] = [gauss[i][0],"under"]
                    ou_list.append([gauss[i][0],"over"])
            else:
                if sign == "+":
                    ou_list[last_j] = [gauss[i][0],"under"]
                    ou_list.append([gauss[i][0],"over"])
                else:
                    ou_list[last_j] = [gauss[i][0],"over"]
                    ou_list.append([gauss[i][0],"under"])           

        else:
            seen.append(gauss[i][0])
            ou_list.append([gauss[i][0],0])
        #print(seen)
    return(ou_list)

# Converts a Plantri-knot to Planer diagram notation
# vertex based --> edge based
def plantri_to_PD(knot):
    ou_list = over_under_list(knot)
    pd_code = []
    for i in range(1, len(knot)+1):
        pd_segment = [-1,-1,-1,-1]
        idx_under = -1
        idx_over = -1
        sign = knot[i-1][2]
        j=0
        while idx_over == -1 or idx_under == -1:
            if ou_list[j][0] == i:
                if ou_list[j][1] == "under":
                    idx_under = j
                else:
                    idx_over = j
            j+=1
        if idx_under == 0:
            idx_under += 2*len(knot)
        if idx_over == 0:
            idx_over += 2*len(knot)
        pd_segment[0] = idx_under
        pd_segment[2] = (idx_under )%(2*len(knot)) + 1
        if sign == "+":
            pd_segment[1] = (idx_over )%(2*len(knot)) + 1
            pd_segment[3] = idx_over
        else:
            pd_segment[1] = idx_over
            pd_segment[3] = (idx_over )%(2*len(knot)) + 1
        pd_code.append(pd_segment)
    return sorted(pd_code)

# 3.Plantri_knots_with_sign --> 5.PD_knots
# converts all knots to PD notation
def PD_knots():
    for i in range(3,11):
        file = open(f"3.Plantri_knots_with_sign/{i}.txt", "r")
        new_file = open(f"5.PD_knots/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            knot = plantri_to_PD(knot)
            new_file.write(f"{knot}\n")
        file.close()
        new_file.close()

# Returns True if a knot in PD notation containts a trivial application of R2
def contains_trivial_R2(knot):
    for i in range(len(knot)):
        if (knot[i][0] + 1)%(2*len(knot)) == (knot[(i+1)%len(knot)][0])%(2*len(knot)):
            temp = knot[i] + knot[(i+1)%len(knot)]
            if len(set(temp)) < 7:
                return True
    return False

# 5.PD_knots --> 6.PD_No_R2
# Removes all knots that contain a trivial application of R2
def remove_trivial_R2():
    for i in range(3,11):
        file = open(f"5.PD_knots/{i}.txt", "r")
        new_file = open(f"6.PD_No_R2/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            if not contains_trivial_R2(knot):
                new_file.write(f"{knot}\n")
        file.close()
        new_file.close()

# Applies R3 on the all triplets of crossings that allows a R3
def apply_R3(knot, log = False):
    knot_list = []
    len_knot = len(knot)
    for i in range(len_knot):
        # look for 2 consecutive understrands
        if (knot[i][0] + 1)%(2*len_knot) == (knot[(i+1)%len_knot][0])%(2*len_knot):
            # look for third crossing of the triangle
            for j in range(len_knot):
                # third crossing cant be either of the first 2
                if knot[j] != knot[i] and knot[j] != knot[(i+1)%len_knot]:
                    # check if it becomes a triangle
                    if knot[i][1] in knot[j] or knot[i][3] in knot[j]:
                        if knot[(i+1)%len_knot][1] in knot[j] or knot[(i+1)%len_knot][3] in knot[j]:
                            # apply R3
                            
                            x = knot[i]
                            y = knot[(i+1)%len_knot]
                            z = knot[j]

                            side = False
                            if (x[1] in z) and (y[1] in z):
                                side = "right"
                            elif (x[3] in z) and (y[3] in z):
                                side = "left"
                            else:
                                print("Side did not resolve properly")
                                break
                            
                            top_left_to_down_right = False
                            if side == "right":
                                if (y[3])%(2*len_knot) == (y[1]+1)%(2*len_knot):
                                    top_left_to_down_right = "left"
                                else:
                                    top_left_to_down_right = "right"
                            else:
                                if (x[3])%(2*len_knot) == (x[1]+1)%(2*len_knot):
                                    top_left_to_down_right = "left"
                                else:
                                    top_left_to_down_right = "right"

                            down_left_to_top_right = False
                            if side == "right":
                                if (x[3])%(2*len_knot) == (x[1]+1)%(2*len_knot):
                                    down_left_to_top_right = "left"
                                else:
                                    down_left_to_top_right = "right"
                            else:
                                if (y[3])%(2*len_knot) == (y[1]+1)%(2*len_knot):
                                    down_left_to_top_right = "left"
                                else:
                                    down_left_to_top_right = "right"

                            
                            part_of_z_understrand = False
                            if side == "right":
                                if (x[1] == z[0]) or (x[1] == z[2]):
                                    part_of_z_understrand = "i"
                                else:
                                    part_of_z_understrand = "i+1"
                            else:
                                if (x[3] == z[0]) or (x[3] == z[2]):
                                    part_of_z_understrand = "i"
                                else:
                                    part_of_z_understrand = "i+1"
                            
                            if side == "right":
                                if down_left_to_top_right == "right":
                                    new_x = [y[0], ((x[1])%(2*len_knot)) + 1, y[2], x[1]]
                                else:
                                    new_x = [y[0], ((x[1] - 2)%(2*len_knot)) + 1, y[2], x[1]]

                                if top_left_to_down_right == "right":
                                    new_y = [x[0], ((y[1])%(2*len_knot)) + 1, x[2], y[1]]
                                else:
                                    new_y = [x[0], ((y[1] - 2)%(2*len_knot)) + 1, x[2], y[1]]

                            else:
                                if top_left_to_down_right == "right":
                                    new_x = [y[0], x[3], y[2], ((x[3] - 2)%(2*len_knot)) + 1]
                                else:
                                    new_x = [y[0], x[3], y[2], ((x[3])%(2*len_knot)) + 1]
                                
                                if down_left_to_top_right == "right":
                                    new_y = [x[0], y[3], x[2], ((y[3] - 2)%(2*len_knot)) + 1]
                                else:
                                    new_y = [x[0], y[3], x[2], ((y[3])%(2*len_knot)) + 1]
                            
                            if side == "right":
                                if part_of_z_understrand == "i":
                                    if down_left_to_top_right == "right":
                                        new_z = [x[3], y[1], x[1], y[3]]
                                    else:
                                        new_z = [x[1], y[3], x[3], y[1]]
                                else:
                                    if top_left_to_down_right == "right":
                                        new_z = [y[3], x[3], y[1], x[1]]
                                    else:
                                        new_z = [y[1], x[1], y[3], x[3]]
                            else:
                                if part_of_z_understrand == "i":
                                    if top_left_to_down_right == "right":
                                        new_z = [x[3], y[3], x[1], y[1]]
                                    else:
                                        new_z = [x[1], y[1], x[3], y[3]]
                                else:
                                    if down_left_to_top_right == "right":
                                        new_z = [y[3], x[1], y[1], x[3]]
                                    else:
                                        new_z = [y[1], x[3], y[3], x[1]]

                            # if (x[0])%(2*len_knot) == (x[2] + 1)%(2*len_knot):
                            #     print("something went wrong, x")
                            # if (y[0])%(2*len_knot) == (y[2] + 1)%(2*len_knot):
                            #     print("something went wrong, y")
                            # if (z[0])%(2*len_knot) == (z[2] + 1)%(2*len_knot):
                            #     print("something went wrong, z")


                            new_knot = knot.copy()
                            new_knot[i] = new_x
                            new_knot[(i+1)%len_knot] = new_y
                            new_knot[j] = new_z

                            if log == True:
                                print(f"x = {x}")
                                print(f"y = {y}")
                                print(f"z = {z}")
                                print(f"new_x = {new_x}")
                                print(f"new_y = {new_y}")
                                print(f"new_z = {new_z}")
                                print(" ")

                            knot_list.append(sorted(new_knot))
                            #return sorted(new_knot)
    return knot_list

# Returns True if a knot in PD notation containts a trivial application of R1
def contains_R1(knot):
    for i in range(len(knot)):
        if len(set(knot[i])) < 4:
            return True
    return False

# Make a list containing all representations of a given knot
# Accounts for relabeling and change of orientation
def all_representations(knot: list):
    all_list = [knot]
    len_knot = len(knot)
    # Accounting for relabeling
    for i in range(1, 2*len_knot):
        knot_copy = copy.deepcopy(all_list[-1])
        knot_copy = [[(x % (2*len_knot)) + 1 for x in sublist] for sublist in knot_copy]
        all_list.append(sorted(knot_copy))

    knot_copy = copy.deepcopy(all_list[-1])
    # Change orientation
    reflected = [[(2*len_knot + 1) - x for x in sublist] for sublist in knot_copy]
    other_orientation = [sublist[2:] + sublist[:2] for sublist in reflected]
    all_list.append(sorted(other_orientation))

    # Accounting for relabeling after changing the orientation
    for i in range(1, 2*len_knot):
        knot_copy = copy.deepcopy(all_list[-1])
        knot_copy = [[(x % (2*len_knot)) + 1 for x in sublist] for sublist in knot_copy]
        all_list.append(sorted(knot_copy))
    
    return all_list

# Transformes a knot into its canonical representation
def canonical_representation(knot: list):
    return sorted(all_representations(knot))[0]

# Continuously applies apply_R3 to a knot to find instances where R1 or R2 is possible
# Returns False if reducible
# Returns the knot in canonical form if not reducible
def deep_search(knot: list, search_depth: int):
    depth = 1
    knot = canonical_representation(knot)

    knot_list = [knot]
    # knot_list = apply_R3(knot)

    while (depth < search_depth):
        depth += 1
        new_list = []
        for new_knot in knot_list:
            R3_list = apply_R3(new_knot)
            for R3_knot in R3_list:
                new_R3_knot = canonical_representation(R3_knot)
                if new_R3_knot in new_list:
                    continue
                new_list.append(new_R3_knot)
        knot_list = new_list


        for new_knot in knot_list:
            if (contains_R1(new_knot)) or (contains_trivial_R2(new_knot)):
                # print(f"Can be reduced at depth: {depth}")
                return False
            
    # print(f"Can not be reduced before depth: {depth}")
    return knot

# 6.PD_No_R2 --> 7.Reduced_knots
# Attempts to find reducible knots through R3
# Prints all knots that can not be reduced (before reaching search_dept) in canonical form
def reduce_knots():
    search_depth = 10
    for i in range(3,11):
        file = open(f"6.PD_No_R2/{i}.txt", "r")
        new_file = open(f"7.Reduced_knots/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            search = deep_search(knot, search_depth)
            if search == False:
                continue
            else:
                new_file.write(f"{search}\n")
        file.close()
        new_file.close()

# Returns the Kauffman bracket Polynomial
def kauffman(knot: list):
    for crossing in knot:
        if len(crossing) == 4:
            # recursivly call kauffman
            knot_a = copy.deepcopy(knot)
            knot_a.remove(crossing)
            knot_a.append([crossing[0], crossing[1]])
            knot_a.append([crossing[2], crossing[3]])

            knot_b = copy.deepcopy(knot)
            knot_b.remove(crossing)
            knot_b.append([crossing[1], crossing[2]])
            knot_b.append([crossing[3], crossing[0]])
            poly = A*kauffman(knot_a) + (A**(-1)) * kauffman(knot_b)
            return expand(poly)
    
    circles = 0
    while len(knot) > 0:
        if len(set(knot[0])) == 1:
            circles += 1
            knot.pop(0)
            continue
        for i in range(1,len(knot)):
            if len(set(knot[0] + knot[i])) == 3:
                new_crossing = list((set(knot[0]) | set(knot[i])) - (set(knot[0]) & set(knot[i])))
                knot.pop(i)
                knot.pop(0)
                knot.append(new_crossing)
                break
            elif len(set(knot[0] + knot[i])) == 2:
                circles += 1
                knot.pop(i)
                knot.pop(0)
                break
        # count circles
    return ((-(A**2) - (A**(-2)))**(circles - 1))

# Returns the Normalized Kauffman bracket Polynomial
def kauffman_normalized(knot: list):
    writhe = 0
    len_knot = len(knot)
    for crossing in knot:
        if (crossing[1])%(2*len_knot) == (crossing[3]+1)%(2*len_knot):
            writhe += 1
        else:
            writhe -= 1
    kauff_part = kauffman(knot)
    return expand((-(A**3))**(-writhe) * kauff_part)

# Returns the Jones polynomial of a knot, using the normalized kauffman bracket
def jones(knot: list):
    kauff = kauffman_normalized(knot)
    return kauff.subs(A, (t)**(Rational(-1,4)))

def print_kauff():
    for i in range(3,9):
        file = open(f"7.Reduced_knots/{i}.txt", "r")
        new_file = open(f"8.knot_and_jones/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)          
            new_file.write(f"{knot}\n")
            kauff = kauffman_normalized(knot)
            new_file.write(f"{kauff.subs(A, (t)**(Rational(-1,4)))}\n")
        file.close()
        new_file.close()

# 7.Reduced_knots --> 9.no_dupes
# Some knots had the same canonical representation and were therefore the same knot
def remove_duplicates():
    for i in range(3,11):
        knot_list = []
        file = open(f"7.Reduced_knots/{i}.txt", "r")
        new_file = open(f"9.no_dupes/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            if knot in knot_list:
                continue
            knot_list.append(knot)
            new_file.write(f"{knot}\n")
        file.close()
        new_file.close()

# returns True if 2-1 pass can be applied (reducible)
# returns False if 2-1 pass can not be applied (non-reducible)
def apply_two_one_pass(knot: list, front: list, end_list: list):
    len_front = len(front)
    end_len = len_front - 2
    next_front = front

    while len(front) != 0:
        # print(front)
        draw_list = []
        skip_next = False
        front = next_front
        len_front = len(front)

        if len_front == end_len:
            return True
        for number in front:
            if number in end_list:
                return False

        # create front and lists what to draw
        for i in range(len_front):
            if skip_next:
                skip_next = False
                continue
            
            if i < len(front) - 1:
                if front[i] == front[i+1]:
                    # semi
                    draw_list.append("cap")

                    skip_next = True
                    next_front.pop(i)
                    next_front.pop(i)
                    continue

                if len(knot) == 0:   
                    draw_list.append("line")
                    continue
                
                found = False
                for crossing in knot:
                    # find other half edge
                    if front[i] in crossing:
                        # bi-gon/cross
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

                            # make a cross
                            if crossing[0] == next_front[i] or crossing[2] == next_front[i]:
                                draw_list.append("cross_under")
                            else:
                                draw_list.append("cross_over")

                            skip_next = True
                            knot.remove(crossing)
                            break
                        else:
                            draw_list.append("line")
                            break
                if not found:
                    draw_list.append("line")
                    continue

            else:              
                draw_list.append("line")
                
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

# returns True if 2-1 pass can be applied (reducible)
# returns False if 2-1 pass can not be applied (non-reducible)
def check_two_one_pass(knot):
    len_knot = len(knot)
    for i in range(len_knot):
        # look for 2 consecutive understrands
        if (knot[i][0] + 1)%(2*len_knot) == (knot[(i+1)%len_knot][0])%(2*len_knot):
            knot_copy = copy.deepcopy(knot)
            crossing_1 = knot_copy[i]
            crossing_2 = knot_copy[(i+1)%len_knot]
            knot_copy.remove(crossing_1)
            knot_copy.remove(crossing_2)
            if apply_two_one_pass(copy.deepcopy(knot_copy), [crossing_1[0], crossing_1[1], crossing_2[1]], [crossing_1[3], crossing_2[3]]):
                return True
            # print(" ")
            if apply_two_one_pass(copy.deepcopy(knot_copy), [crossing_1[1], crossing_2[1], crossing_2[2]], [crossing_1[3], crossing_2[3]]):
                return True
            # print(" ")
            if apply_two_one_pass(copy.deepcopy(knot_copy), [crossing_2[2], crossing_2[3], crossing_1[3]], [crossing_1[1], crossing_2[1]]):
                return True
            # print(" ")
            if apply_two_one_pass(copy.deepcopy(knot_copy), [crossing_2[3], crossing_1[3], crossing_1[0]], [crossing_1[1], crossing_2[1]]):
                return True
    return False

# 9.no_dupes --> 10.pass_reduced
def reduce_by_pass():
    for i in range(3,11):
        file = open(f"9.no_dupes/{i}.txt", "r")
        new_file = open(f"10.pass_reduced/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            if check_two_one_pass(knot):
                continue
            new_file.write(f"{knot}\n")
        file.close()
        new_file.close()

# knot in pd code --> knot in [sign_1,overpass_1,underpass_1] parts
def pd_to_sign_over_under(knot):
    sou = []
    len_knot = 2*len(knot)
    for crossing in knot:
        if (crossing[1])%len_knot == (crossing[3])%len_knot+1:
            sou.append([1,crossing[3]%len_knot , crossing[0]%len_knot])
        else:
            sou.append([-1,crossing[1]%len_knot , crossing[0]%len_knot])
    return sou

# knot in sou-code --> Rotation numbers
def rotation_numbers(knot: list):   
    len_knot = len(knot)
    rot_list = [0 for _ in range(2 * len_knot + 1)]

    for crossing in knot:
        if crossing[0] == -1:
            crossing[1], crossing[2] = crossing[2], crossing[1]
        crossing.pop(0)
        if crossing[0] == 0:
            crossing[0] = 2*len_knot
        if crossing[1] == 0:
            crossing[1] = 2*len_knot

    # print(knot)
    front = [[1, "u"]]
    knot_done = False
    # rot_list[knot[0][0] - 1]  = 1

    # print(rot_list)

    len_front = len(front)    
    
    next_front = front
    while not knot_done:
        if (len(front) == 1) and (len(knot) == 0):
            knot_done = True
            break

        # print(front)

        draw_list = []
        skip_next = False
        front = next_front
        len_front = len(front)

        # create front and lists what to draw
        for i in range(len_front):
            if skip_next:
                skip_next = False
                continue
            
            if i < len(front) - 1:
                if front[i][0] == front[i+1][0]:
                    draw_list.append("cap")
                    skip_next = True
                    if front[i][1] == "d": #if cap is to the right
                        rot_list[front[i][0] - 1] = rot_list[front[i][0] - 1] -1
                    next_front.pop(i)
                    next_front.pop(i)
                    continue

                if len(knot) == 0:   
                    # draw a line
                    draw_list.append("line")
                    continue
                
                found = False
                for crossing in knot:
                    # find other half edge
                    if front[i][0] in crossing:
                        # bi-gon/cross
                        found = True
                
                        if front[i+1][0] in crossing:
                            # update front
                            next_front[i] = [(crossing[0])%(2*len_knot) + 1, "u"]
                            next_front[i+1] = [(crossing[1])%(2*len_knot) + 1, "u"]


                            # make a cross
                            draw_list.append("cross")

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
                    if front[i][0] in crossing:
                        if front[i][0] == crossing[0]:
                            next_front[i] = [(crossing[1]%(2*len_knot)) + 1, "u"]
                            next_front.insert(i, [(crossing[0]%(2*len_knot)) + 1, "u"])
                            next_front.insert(i, [crossing[1], "d"])
                        else: # front[i][0] == crossing[0]
                            next_front[i] = [(crossing[0]%(2*len_knot)) + 1, "u"]
                            next_front.insert(i+1, [crossing[0], "d"])
                            next_front.insert(i+1, [(crossing[1]%(2*len_knot)) + 1, "u"])
                            rot_list[crossing[0] - 1] += 1

                        knot.remove(crossing)

                        done = True
                        break
    return rot_list

        

def theta(knot = []):
    # Cs = pd_to_sign_over_under(knot)
    # phi = rotation_numbers(Cs)
    

    # Trefoil
    Cs=[[1,0,3],[1,4,1],[1,2,5]]
    phi=[0,0,0,-1,0,0,0]
    
    # Knot 8_15 input
    # Cs=[[-1, 3, 0], [-1, 7, 2], [-1, 11, 4], [-1, 15, 12], [-1, 13, 8], [-1, 9, 14], [-1, 5, 10], [-1, 1, 6]]
    # phi=[0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 1, -1, 0, -1, 0, 0, 0]

    #knot 11n42
    # Cs=[[1, 0, 3], [1, 2, 7], [-1, 4, 11], [1, 6, 1], [-1, 17,8], [1, 19, 10], [-1, 12, 5], [-1, 9, 14], [-1, 21, 16], [1, 13, 18],[-1, 15, 20]]
    # phi=[0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,0, -1, 0, 0, 0, 0, 0]

   
    n = len(Cs)
    size = 2 * n + 1

    # Initialize matrix A1
    A1 = eye(size)

    # Populate A1 matrix
    for c in Cs:
        sign, i, j = c
        A1[i, i+1] = -t1**sign
        A1[i, j+1] = t1**sign - 1
        A1[j, j+1] = -1

    # Determinants
    total_phi = sum(phi)
    total_signs = sum(c[0] for c in Cs)
    Delta1 = t1**((-total_phi - total_signs)/2) * A1.det()
    Delta2 = Delta1.subs(t1, t2)
    Delta3 = Delta1.subs(t1, t1 * t2)

    # Inverses
    G1 = A1.inv()
    G2 = G1.subs(t1, t2)
    G3 = G1.subs(t1, t1 * t2)

    # Functions
    def F11(s, i, j):
        return s * (
            Rational(1, 2) +
            t2**s * G1[i, i] * G2[j, i] +
            ((t1**s - 1) * t2**(2*s) * G1[j, i] * G2[j, i]) / (t2**s - 1) -
            G1[i, i] * G2[j, j] -
            (t1**s - 1) * t2**s * G1[j, i] * G2[j, j] / (t2**s - 1) -
            G3[i, i] -
            (t2**s - 1) * G2[j, i] * G3[i, i] +
            2 * G2[j, j] * G3[i, i] +
            (t1**s * t2**s - 1) * G3[j, i] / (t2**s - 1) -
            t2**s * (t1**s * t2**s - 1) * G1[i, i] * G3[j, i] / (t2**s - 1) -
            (t1**s - 1) * (t2**s + 1) * (t1**s * t2**s - 1) * G1[j, i] * G3[j, i] / (t2**s - 1) +
            (t1**s * t2**s - 1) * G2[i, j] * G3[j, i] / (t2**s - 1) +
            (t1**s * t2**s - 1) * G2[j, i] * G3[j, i] +
            (t2**s - 2) * (t1**s * t2**s - 1) * G2[j, j] * G3[j, i] / (t2**s - 1) +
            G1[i, i] * G3[j, j] +
            (t1**s - 1) * t2**s * G1[j, i] * G3[j, j] / (t2**s - 1) -
            G2[i, i] * G3[j, j] -
            t2**s * G2[j, i] * G3[j, j]
        )

    def F12(s0, i0, j0, s1, i1, j1):
        numerator = (t1**s0 - 1) * (t1**s1 * t2**s1 - 1) * G1[j1, i0] * G3[j0, i1] * (
            t2**s0 * G2[i1, i0]
            - G2[i1, j0]
            - t2**s0 * G2[j1, i0]
            + G2[j1, j0]
        )
        return s1 * numerator / (t2**s1 - 1)

    def Gam1(ph, k):
        return ph * G3[k, k] - ph / 2

    # Theta computation
    theta = 0
    for c in Cs:
        theta += F11(c[0], c[1], c[2])
    for c1 in Cs:
        for c2 in Cs:
            theta += F12(c1[0], c1[1], c1[2], c2[0], c2[1], c2[2])
    for k in range(size):
        theta += Gam1(phi[k], k)

    # Final expression
    theta = theta * Delta1 * Delta2 * Delta3
    # theta_simplified = simplify(theta)
    # return nsimplify(theta_simplified, rational=True)
    return theta.subs({t1: pi, t2: e}).evalf()


if __name__ == "__main__":
    # reduce_by_pass()

    # with timer("Theta()"):
    #     result = print(theta())

    # print(theta())
     
 
    # sou = pd_to_sign_over_under(knot)
    # print(sou)
    # print(rotation_numbers(sou))


    knot = [[1, [2, 3, 4, 5]], [2, [1, 6, 6, 3]], [3, [1, 2, 6, 4]], [4, [1, 3, 5, 5]], [5, [1, 4, 4, 6]], [6, [2, 5, 3, 2]]]
    print(get_gauss(knot))

    # print(jones(knot))
    # print(pd_to_sign_over_under(knot))
    # print(jones(knot))
    # for i in range(5):
    #     sou = pd_to_sign_over_under(knot)
    #     random.shuffle(sou)
    #     print(sou)
    #     print(rotation_numbers(sou))

    # random.shuffle(knot)
    # print(knot)

    # canonical_representation()
    
    # file = open(f"10.pass_reduced/{8}.txt", "r")
    # for line in file:
    #     knot = ast.literal_eval(line)
    #     print(knot)
    #     print(jones(knot))
        

















    7_1
    [[1, 9, 2, 8], [3, 11, 4, 10], [5, 13, 6, 12], [7, 1, 8, 14], [9, 3, 10, 2], [11, 5, 12, 4], [13, 7, 14, 6]]
    -t**10 + t**9 - t**8 + t**7 - t**6 + t**5 + t**3
    [[1, 8, 2, 9], [3, 10, 4, 11], [5, 12, 6, 13], [7, 14, 8, 1], [9, 2, 10, 3], [11, 4, 12, 5], [13, 6, 14, 7]]
    t**(-3) + t**(-5) - 1/t**6 + t**(-7) - 1/t**8 + t**(-9) - 1/t**10

    7_2
    [[1, 5, 2, 4], [3, 11, 4, 10], [5, 1, 6, 14], [7, 13, 8, 12], [9, 3, 10, 2], [11, 9, 12, 8], [13, 7, 14, 6]]
    -t**8 + t**7 - t**6 + 2*t**5 - 2*t**4 + 2*t**3 - t**2 + t
    [[1, 4, 2, 5], [3, 10, 4, 11], [5, 14, 6, 1], [7, 12, 8, 13], [9, 2, 10, 3], [11, 8, 12, 9], [13, 6, 14, 7]]
    1/t - 1/t**2 + 2/t**3 - 2/t**4 + 2/t**5 - 1/t**6 + t**(-7) - 1/t**8

    7_3
    [[1, 7, 2, 6], [3, 11, 4, 10], [5, 13, 6, 12], [7, 1, 8, 14], [9, 3, 10, 2], [11, 5, 12, 4], [13, 9, 14, 8]]
    -t**9 + t**8 - 2*t**7 + 3*t**6 - 2*t**5 + 2*t**4 - t**3 + t**2
    [[1, 6, 2, 7], [3, 10, 4, 11], [5, 12, 6, 13], [7, 14, 8, 1], [9, 2, 10, 3], [11, 4, 12, 5], [13, 8, 14, 9]]
    t**(-2) - 1/t**3 + 2/t**4 - 2/t**5 + 3/t**6 - 2/t**7 + t**(-8) - 1/t**9

    7_5
    [[1, 5, 2, 4], [3, 11, 4, 10], [5, 13, 6, 12], [7, 1, 8, 14], [9, 3, 10, 2], [11, 9, 12, 8], [13, 7, 14, 6]]
    -t**9 + 2*t**8 - 3*t**7 + 3*t**6 - 3*t**5 + 3*t**4 - t**3 + t**2
    [[1, 4, 2, 5], [3, 10, 4, 11], [5, 12, 6, 13], [7, 14, 8, 1], [9, 2, 10, 3], [11, 8, 12, 9], [13, 6, 14, 7]]
    t**(-2) - 1/t**3 + 3/t**4 - 3/t**5 + 3/t**6 - 3/t**7 + 2/t**8 - 1/t**9
    [[1, 5, 2, 4], [3, 11, 4, 10], [5, 1, 6, 14], [7, 13, 8, 12], [9, 3, 10, 2], [11, 7, 12, 6], [13, 9, 14, 8]]
    -t**9 + 2*t**8 - 3*t**7 + 3*t**6 - 3*t**5 + 3*t**4 - t**3 + t**2
    [[1, 4, 2, 5], [3, 10, 4, 11], [5, 14, 6, 1], [7, 12, 8, 13], [9, 2, 10, 3], [11, 6, 12, 7], [13, 8, 14, 9]]
    t**(-2) - 1/t**3 + 3/t**4 - 3/t**5 + 3/t**6 - 3/t**7 + 2/t**8 - 1/t**9

    7_6
    [[1, 4, 2, 5], [3, 9, 4, 8], [5, 13, 6, 12], [7, 10, 8, 11], [9, 3, 10, 2], [11, 1, 12, 14], [13, 7, 14, 6]]
    -t**6 + 2*t**5 - 3*t**4 + 4*t**3 - 3*t**2 + 3*t - 2 + 1/t
    [[1, 4, 2, 5], [3, 10, 4, 11], [5, 9, 6, 8], [7, 12, 8, 13], [9, 2, 10, 3], [11, 1, 12, 14], [13, 6, 14, 7]]
    t - 2 + 3/t - 3/t**2 + 4/t**3 - 3/t**4 + 2/t**5 - 1/t**6
    [[1, 4, 2, 5], [3, 9, 4, 8], [5, 14, 6, 1], [7, 13, 8, 12], [9, 3, 10, 2], [11, 7, 12, 6], [13, 11, 14, 10]]
    -t**6 + 2*t**5 - 3*t**4 + 4*t**3 - 3*t**2 + 3*t - 2 + 1/t
    [[1, 4, 2, 5], [3, 12, 4, 13], [5, 11, 6, 10], [7, 14, 8, 1], [9, 7, 10, 6], [11, 2, 12, 3], [13, 8, 14, 9]]
    t - 2 + 3/t - 3/t**2 + 4/t**3 - 3/t**4 + 2/t**5 - 1/t**6

    7_4
    [[1, 7, 2, 6], [3, 11, 4, 10], [5, 13, 6, 12], [7, 1, 8, 14], [9, 5, 10, 4], [11, 3, 12, 2], [13, 9, 14, 8]]
    -t**8 + t**7 - 2*t**6 + 3*t**5 - 2*t**4 + 3*t**3 - 2*t**2 + t
    [[1, 6, 2, 7], [3, 10, 4, 11], [5, 12, 6, 13], [7, 14, 8, 1], [9, 4, 10, 5], [11, 2, 12, 3], [13, 8, 14, 9]]
    1/t - 2/t**2 + 3/t**3 - 2/t**4 + 3/t**5 - 2/t**6 + t**(-7) - 1/t**8

    7_7
    [[1, 4, 2, 5], [3, 11, 4, 10], [5, 12, 6, 13], [7, 1, 8, 14], [9, 6, 10, 7], [11, 3, 12, 2], [13, 9, 14, 8]]
    t**4 - 2*t**3 + 3*t**2 - 4*t + 4 - 3/t + 3/t**2 - 1/t**3
    [[1, 4, 2, 5], [3, 9, 4, 8], [5, 10, 6, 11], [7, 13, 8, 12], [9, 3, 10, 2], [11, 14, 12, 1], [13, 7, 14, 6]]
    t**4 - 2*t**3 + 3*t**2 - 4*t + 4 - 3/t + 3/t**2 - 1/t**3
    [[1, 5, 2, 4], [3, 8, 4, 9], [5, 12, 6, 13], [7, 1, 8, 14], [9, 2, 10, 3], [11, 6, 12, 7], [13, 11, 14, 10]]
    -t**3 + 3*t**2 - 3*t + 4 - 4/t + 3/t**2 - 2/t**3 + t**(-4)
    [[1, 5, 2, 4], [3, 8, 4, 9], [5, 11, 6, 10], [7, 12, 8, 13], [9, 2, 10, 3], [11, 1, 12, 14], [13, 6, 14, 7]]
    -t**3 + 3*t**2 - 3*t + 4 - 4/t + 3/t**2 - 2/t**3 + t**(-4)



    


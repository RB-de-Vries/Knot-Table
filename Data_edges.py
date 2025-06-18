import re
import ast
import copy
from sympy import *
from symengine import symbols, Rational, eye
from math import pi, e
from pickle import dump, load

A, t = symbols("A t")
t1, t2 = symbols("t1 t2")
theta_bound = 1*(10**(-2))

# Reads Plantri output, returns the data as proper nested lists
def Read_Plantri_Data(s: str) -> list[list[int]]:
    pattern = re.findall(r'(\d+)\[(.*?)\]', s)
    result = []
    
    for key, values in pattern:
        # Convert space-separated numbers to a list of integers
        numbers = list(map(int, values.split()))  
        result.append([int(key), numbers])
    
    return result

# Knot in plantri-format --> Gauss-like code 
def get_gauss(knot: list[list[int]]):
    # Start point
    gauss = [[1, 0]]

    # Start by choosing into the direction of knot[0][1][0] Ususally 2
    crossing = knot[0][1]
    # If 2 appears once
    if crossing.count(crossing[0]) == 1:
        gauss.append([crossing[0], 1])
    # If 2 appears twice
    else:
        if crossing[1] == crossing[0]:
            gauss.append([crossing[0], "-"])
        else:
            gauss.append([crossing[0], "+"])

    done = False
    while not done:
        # Pick the next crossing
        next_crossing = knot[gauss[-1][0] - 1][1] # -1 because 0-indexing
        index = next_crossing.index(gauss[-2][0])
        # If the next value is not unique, find where we came from
        if next_crossing.count(gauss[-2][0]) != 1:
            if gauss[-1][1] == "-":
                if next_crossing[index] == next_crossing[index + 1]:
                    index += 1
            else:
                if next_crossing[index] != next_crossing[index + 1]:
                    index = 3

        # If where we go to is unique, write it
        if next_crossing.count(next_crossing[(index + 2) % 4]) == 1:
            gauss.append([next_crossing[(index + 2) % 4], gauss[-1][0]])
        # Else, find where we go to
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
    for i in range(3,11):
        count = 0
        file = open(f"1.Plantri_Data/{i}.txt", "r")
        new_file = open(f"2.Plantri_knots/{i}.txt", "w")
        for line in file:
            knot = Read_Plantri_Data(line.rstrip()[3:])
            gauss_code = get_gauss(knot)
            if len(gauss_code) == ((len(knot)*2) + 2):
                new_file.write(f"{knot}\n")
                count += 1

# 2.Plantri_knots --> 3.Plantri_knots_with_sign
# Adds a sign to each crossing (all combinations)
def add_sign_to_crossing():
    def print_binary_sequences(n, knot):
        if n < 0:
            new_file.write(f"{knot}\n")
        else:
            # Recursively call this function untill the knot is filled in
            knot_1 = copy.deepcopy(knot)
            knot_1[n].append("+")
            print_binary_sequences(n - 1, knot_1)
            knot_2 = copy.deepcopy(knot)
            knot_2[n].append("-")
            print_binary_sequences(n - 1, knot_2)

    # Go through each file and line to apply print_binary_sequences()
    for i in range(3,11):
        file = open(f"2.Plantri_knots/{i}.txt", "r")
        new_file = open(f"3.Plantri_knots_with_sign/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            print_binary_sequences(i-1, knot)
        file.close()
        new_file.close()

# Returns a list following the knot, listing if the crossing goes over or under
def over_under_list(knot):
    ou_list = []
    seen = []
    gauss = get_gauss(knot)
    # Loop over the Gauss list (without the two duplicates at the end of the list)
    for i in range(0,len(gauss) - 2):
        # If we have seen this vertex before
        if gauss[i][0] in seen:
            crossing = knot[gauss[i][0] - 1][1]
            sign = knot[gauss[i][0]-1][2]
            idx_first = -1
            idx_second = -1
            last_j = -1
            # Find the vertex in the list that we have seen before
            for j in range(len(gauss) - 2):
                if gauss[j][0] == gauss[i][0]:
                    # If that previous vertex had a duplicate entry, there is a "+" or "-" we need to account for
                    if isinstance(gauss[j+1][1], str):
                        if gauss[j+1][1] == "+":
                            idx_first = crossing.index(gauss[j+1][0])
                            if idx_first != 0:
                                idx_first += 1
                            last_j = j
                            break
                        else:
                            idx_first = crossing.index(gauss[j+1][0])
                            if idx_first == 0:
                                if crossing[1] != gauss[j+1][0]:
                                    idx_first = 3
                            last_j = j
                            break
                    else:
                        idx_first = crossing.index(gauss[j+1][0])
                        last_j = j
                        break
            # If the new vertex has a duplicate entry, there is a "+" or "-" we need to account for
            if isinstance(gauss[i+1][1],str):
                if gauss[i+1][1] == "+":
                    idx_second = crossing.index(gauss[i+1][0])
                    if idx_second != 0:
                        idx_second += 1
                else:
                    idx_second = crossing.index(gauss[i+1][0])
                    if idx_second == 0:
                        if crossing[1] != gauss[i+1][0]:
                                idx_second = 3
            else:
                idx_second = crossing.index(gauss[i+1][0])
        
            # Decide if we go over or under for both the previous instance and the current one
            if idx_first == ((idx_second + 1)%4):
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

        # If we have not seen this vertex
        else:
            # Add it to both lists
            seen.append(gauss[i][0])
            # The 0 here is a dummy value
            ou_list.append([gauss[i][0],0])

    return(ou_list)

# Converts a Plantri-knot to Planer diagram notation
# vertex based --> edge based
def plantri_to_PD(knot):
    ou_list = over_under_list(knot)
    pd_code = []
    # We want the code to not contain the the number 0
    for i in range(1, len(knot)+1):
        pd_segment = [-1,-1,-1,-1]
        idx_under = -1
        idx_over = -1
        sign = knot[i-1][2]
        # find the other strand of the crossing
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
        # Fill in pd-code
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

# 3.Plantri_knots_with_sign --> 4.PD_knots
# converts all knots to PD notation
def PD_knots():
    for i in range(3,11):
        file = open(f"3.Plantri_knots_with_sign/{i}.txt", "r")
        new_file = open(f"4.PD_knots/{i}.txt", "w")
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

# 4.PD_knots --> 5.PD_No_R2
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
def apply_R3(knot):
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

                            # deduce the specific r3 application we have
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
                            
                            # apply r3 based on the specific application
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

                            # replace the previous three crossings with the new ones
                            new_knot = knot.copy()
                            new_knot[i] = new_x
                            new_knot[(i+1)%len_knot] = new_y
                            new_knot[j] = new_z
                            
                            knot_list.append(sorted(new_knot))
    return knot_list

# Returns True if a knot in PD notation contains a trivial application of R1
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
def deep_R3_search(knot: list, search_depth: int):
    depth = 1
    knot = canonical_representation(knot)
    knot_list = [knot]

    # Search untill the desired depth
    while (depth < search_depth):
        depth += 1
        new_list = []
        # Fill list with all unique application of R3
        for new_knot in knot_list:
            R3_list = apply_R3(new_knot)
            for R3_knot in R3_list:
                new_R3_knot = canonical_representation(R3_knot)
                if new_R3_knot in new_list:
                    continue
                new_list.append(new_R3_knot)
        knot_list = new_list

        # If the knot is reducible (by R1 or R2) we are done
        for new_knot in knot_list:
            if (contains_R1(new_knot)) or (contains_trivial_R2(new_knot)):
                return False
            
    # We assume the knot to be non-reducible
    return knot

# 5.PD_No_R2 --> 6.Reduced_knots
# Attempts to find reducible knots through R3
# Prints all knots that can not be reduced (before reaching search_dept) in canonical form
def reduce_knots_by_R3():
    search_depth = 10
    for i in range(3,11):
        file = open(f"6.PD_No_R2/{i}.txt", "r")
        new_file = open(f"7.Reduced_knots/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            search = deep_R3_search(knot, search_depth)
            if search == False:
                continue
            else:
                new_file.write(f"{search}\n")
        file.close()
        new_file.close()

# 6.Reduced_knots --> 7.no_dupes
# Some knots had the same canonical representation and were therefore the same knot
def remove_duplicates():
    for i in range(3,11):
        knot_list = []
        file = open(f"6.Reduced_knots/{i}.txt", "r")
        new_file = open(f"7.no_dupes/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            if knot in knot_list:
                continue
            knot_list.append(knot)
            new_file.write(f"{knot}\n")
        file.close()
        new_file.close()

# Constucts knot to check if a 2-1 pass is valid from a specific location
def is_two_one_pass_valid(knot: list, front: list, end_list: list):
    len_front = len(front)
    end_len = len_front - 2
    next_front = front

    while len(front) != 0:
        draw_list = []
        skip_next = False
        front = next_front
        len_front = len(front)

        # We are done if our front is of lenght 1
        if len_front == end_len:
            return True
        # or if our front contains a number that it shouldnt (exampe: otherside of startfront)
        for number in front:
            if number in end_list:
                return False

        # create next front and draw list
        for i in range(len_front):
            # skip next number if we have placed cap/cross
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
                
                # no placable knots = only caps and lines can be drawn
                if len(knot) == 0:   
                    draw_list.append("line")
                    continue
                
                found = False
                for crossing in knot:
                    # find other half edge
                    if front[i] in crossing:
                        found = True
                        # can we place cross?
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
                        draw_list[i] = "fork"
                        done = True
                        break

# Checks all cases where 2-1 might be applicable
# returns True if 2-1 pass can be applied, False otherwise
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
            # Given two consecutive understrands, there are four cases to check for 2-1 pass
            if is_two_one_pass_valid(copy.deepcopy(knot_copy), [crossing_1[0], crossing_1[1], crossing_2[1]], [crossing_1[3], crossing_2[3]]):
                return True
            if is_two_one_pass_valid(copy.deepcopy(knot_copy), [crossing_1[1], crossing_2[1], crossing_2[2]], [crossing_1[3], crossing_2[3]]):
                return True
            if is_two_one_pass_valid(copy.deepcopy(knot_copy), [crossing_2[2], crossing_2[3], crossing_1[3]], [crossing_1[1], crossing_2[1]]):
                return True
            if is_two_one_pass_valid(copy.deepcopy(knot_copy), [crossing_2[3], crossing_1[3], crossing_1[0]], [crossing_1[1], crossing_2[1]]):
                return True
    return False

# 7.no_dupes --> 8.pass_reduced
def reduce_by_pass():
    for i in range(3,11):
        file = open(f"7.no_dupes/{i}.txt", "r")
        new_file = open(f"8.pass_reduced/{i}.txt", "w")
        for line in file:
            knot = ast.literal_eval(line)
            if check_two_one_pass(knot):
                continue
            new_file.write(f"{knot}\n")
        file.close()
        new_file.close()

# Returns the Kauffman bracket Polynomial
def kauffman(knot: list):
    # Break down crossings to line segments
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
    # Count the amount of circles you can form with the line segments
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
    return ((-(A**2) - (A**(-2)))**(circles - 1))

# Returns the Normalized Kauffman bracket Polynomial
def kauffman_normalized(knot: list):
    writhe = 0
    len_knot = len(knot)
    # Calculate the Writhe of a knot
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

# knot in pd code --> knot in [sign_i,overpass_i,underpass_i] parts
def pd_to_sign_over_under(knot):
    sou = []
    len_knot = 2*len(knot)
    for crossing in knot:
        if (crossing[1]-1)%len_knot+1 == (crossing[3])%len_knot+1:
            sou.append([1,(crossing[3]-1)%len_knot , (crossing[0]-1)%len_knot])
        else:
            sou.append([-1, (crossing[1]-1)%len_knot,(crossing[0]-1)%len_knot])
    return sou

# knot in sou-code --> Rotation numbers
def rotation_numbers(knot: list):   
    len_knot = len(knot)
    rot_list = [0 for _ in range(2 * len_knot + 1)]

    # Removeing the sign and changing the orden for negative crossings
    # This makes looping through the crossings to place them easier
    for crossing in knot:
        if crossing[0] == -1:
            crossing[1], crossing[2] = crossing[2], crossing[1]
        crossing.pop(0)

    # Startpoint
    front = [[0, "u"]]
    knot_done = False
    
    len_front = len(front)    
    
    next_front = front
    while not knot_done:
        # Our stop condition is haveing a front of size 1 AND haveing used all knots 
        if (len(front) == 1) and (len(knot) == 0):
            knot_done = True
            break

        draw_list = []
        skip_next = False
        front = next_front
        len_front = len(front)

        # create front and lists what to draw
        for i in range(len_front):
            # skip next number if we have placed cap/cross
            if skip_next:
                skip_next = False
                continue
            
            if i < len(front) - 1:
                # can we place a cap?
                if front[i][0] == front[i+1][0]:
                    draw_list.append("cap")
                    skip_next = True
                    #If cap is to the right, we update the rotation number
                    if front[i][1] == "d": 
                        rot_list[front[i][0]] -= 1
                    next_front.pop(i)
                    next_front.pop(i)
                    continue
                
                # no placable knots = only caps and lines can be drawn
                if len(knot) == 0:   
                    draw_list.append("line")
                    continue
                
                found = False
                for crossing in knot:
                    # find other half edge
                    if front[i][0] in crossing:
                        found = True
                        # can we place cross?
                        if front[i+1][0] in crossing:
                            next_front[i] = [(crossing[0])%(2*len_knot) + 1, "u"]
                            next_front[i+1] = [(crossing[1])%(2*len_knot) + 1, "u"]

                            # make a cross
                            draw_list.append("cross")

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
        
        # If we can only draw lines with the rules above, we need to place a cup + cross
        if len(set(draw_list)) == 1 and draw_list[0] == "line":
            done = False
            for i in range(len(front)):
                if done:
                    done = False
                    break
                for crossing in knot:
                    if front[i][0] in crossing:
                        # Do we place cup + cross on the right?
                        if front[i][0] == crossing[0]:
                            next_front[i] = [(crossing[1]%(2*len_knot)) + 1, "u"]
                            next_front.insert(i, [(crossing[0]%(2*len_knot)) + 1, "u"])
                            next_front.insert(i, [crossing[1], "d"])
                        else: 
                            next_front[i] = [(crossing[0]%(2*len_knot)) + 1, "u"]
                            next_front.insert(i+1, [crossing[0], "d"])
                            next_front.insert(i+1, [(crossing[1]%(2*len_knot)) + 1, "u"])
                            rot_list[crossing[0]] += 1

                        knot.remove(crossing)

                        done = True
                        break
    return rot_list
        
# Computes the Theta invariant at t_1 = pi, t_2 = e
def theta(knot: list):
    Cs = pd_to_sign_over_under(knot)
    phi = rotation_numbers(copy.deepcopy(Cs))
   
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
            Rational(1, 2) + t2**s * G1[i, i] * G2[j, i] +
            ((t1**s - 1) * t2**(2*s) * G1[j, i] * G2[j, i]) / (t2**s - 1) -
            G1[i, i] * G2[j, j] -
            (t1**s - 1) * t2**s * G1[j, i] * G2[j, j] / (t2**s - 1) -
            G3[i, i] - (t2**s - 1) * G2[j, i] * G3[i, i] +
            2 * G2[j, j] * G3[i, i] +
            (t1**s * t2**s - 1) * G3[j, i] / (t2**s - 1) -
            t2**s * (t1**s * t2**s - 1) * G1[i, i] * G3[j, i] / (t2**s - 1) -
            (t1**s - 1) * (t2**s + 1) * (t1**s * t2**s - 1) * G1[j, i] * G3[j, i] / (t2**s - 1) +
            (t1**s * t2**s - 1) * G2[i, j] * G3[j, i] / (t2**s - 1) +
            (t1**s * t2**s - 1) * G2[j, i] * G3[j, i] +
            (t2**s - 2) * (t1**s * t2**s - 1) * G2[j, j] * G3[j, i] / (t2**s - 1) +
            G1[i, i] * G3[j, j] +
            (t1**s - 1) * t2**s * G1[j, i] * G3[j, j] / (t2**s - 1) -
            G2[i, i] * G3[j, j] -t2**s * G2[j, i] * G3[j, j]
        )

    def F12(s0, i0, j0, s1, i1, j1):
        numerator = (t1**s0 - 1) * (t1**s1 * t2**s1 - 1) * G1[j1, i0] * G3[j0, i1] * (
            t2**s0 * G2[i1, i0] - G2[i1, j0] - t2**s0 * G2[j1, i0] + G2[j1, j0]
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
    return theta.subs({t1: pi, t2: e}).evalf()

# Find a bound for theta to be able to compare theta values
def find_theta_bound():
    smallest = 1000000
    max_diff = 0
    file = open(f"8.pass_reduced/{8}.txt", "r")
    for line in file:
        knot = ast.literal_eval(line)         
        knot_list = all_representations(knot)
        theta_list = []
        # Find theta of all prepresentations
        for knot in knot_list:
            theta_list.append(theta(knot))
        # Find the biggest difference
        diff = max(theta_list) - min(theta_list)
        jones_poly = jones(knot)
        # Keep track of biggest difference and smallest absolute
        if abs(min(theta_list)) < smallest:
            if jones_poly.subs(t, 1/t) != jones_poly:
                smallest = abs(min(theta_list))
        if diff > max_diff:
            max_diff = diff
    print("max diff:", diff)
    print("Smallest absolut:", smallest)

# Given knot and startpoint, rebuild the knot and apply flype transformation
def apply_flype(knot: list[list[int]], front: list, end_list, directions, sign):
    start_front = copy.deepcopy(front)
    crossings_to_flip = []
    len_knot = len(knot) + 1
    len_front = len(front)
    end_len = 2
    first_step = True
    next_front = front

    while len(front) != 0:
        # print(front)
        draw_list = []
        skip_next = False
        front = next_front
        len_front = len(front)

        # Check conditions to stop looping
        if len_front == end_len:
            if first_step == False:
                end_front = front
                break
        first_step = False
        for number in front:
            if number in end_list:
                return False

        # Create front and lists what to draw
        for i in range(len_front):
            if skip_next:
                skip_next = False
                continue
            
            if i < len(front) - 1:
                # Can we apply a cap?
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
                        found = True
                        # Can we place a cross?
                        if front[i+1] in crossing:
                            # place the cross
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
                            crossings_to_flip.append(crossing)
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
                        crossings_to_flip.append(crossing)
                        knot.remove(crossing)
                        draw_list[i] = "fork"
                        done = True
                        break
    
    # Apply the flype transformation
    for crossing in crossings_to_flip:
        # Flip the order
        crossing[1], crossing[3] = crossing[3], crossing[1]
        # Ensure that the Flip produces a valid PD code
        if (crossing[1]%(2*len_knot)) + 1 ==  crossing[3]:
            crossing = crossing[1:] + crossing[:1]
        else: 
            crossing = crossing[3:] + crossing[:3]

        # All crossings that are flipped need to be relabled aswell
        if directions == "rr":
            for idx, number in enumerate(crossing):
                crossing[idx] = (number - 2)%(2*len_knot) + 1
        elif directions == "ll":
            for idx, number in enumerate(crossing):
                crossing[idx] = (number)%(2*len_knot) + 1
        else:
            right_dir_idx = -1
            start_front_idx = -1
            if directions == "rl":
                start_front_idx = 1
            else:
                start_front_idx = 0
            
            for i in range(2*len_knot):
                if (start_front[start_front_idx] + i-1)%(2*len_knot) + 1 in end_front:
                    right_dir_idx = end_front.index((start_front[start_front_idx] + i-1)%(2*len_knot) + 1)
                    break
                # Skip over a specific case that is significantly harder to implement then the rest
                if (start_front[start_front_idx] + i-1)%(2*len_knot) + 1 == start_front[(start_front_idx + 1 )%2]:
                    return False
                
            if start_front[start_front_idx] < end_front[right_dir_idx]:
                for idx, number in enumerate(crossing):
                    if start_front[start_front_idx] <= number <= end_front[right_dir_idx]:
                        crossing[idx] = (number - 2)%(2*len_knot) + 1
                    else:
                        crossing[idx] = (number)%(2*len_knot) + 1
            else:
                for idx, number in enumerate(crossing):
                    if number >= start_front[start_front_idx] or end_front[right_dir_idx]>= number:   
                    # if number <= start_front[start_front_idx] or end_front[right_dir_idx]<= number:
                        crossing[idx] = (number - 2)%(2*len_knot) + 1
                    else:
                        crossing[idx] = (number)%(2*len_knot) + 1

        knot.append(crossing)

    # Add the crossing on the other side of the flipped crossings
    if directions == "rr":
        if sign == "+":
            knot.append([(end_front[1] - 2)%(2*len_knot) + 1, end_front[0], end_front[1], (end_front[0] - 2)%(2*len_knot) + 1])
        else:
            knot.append([(end_front[0] - 2)%(2*len_knot) + 1, (end_front[1] - 2)%(2*len_knot) + 1, end_front[0], end_front[1]])
    elif directions == "ll":
        if sign == "+":
            knot.append([end_front[1], (end_front[0])%(2*len_knot) + 1, (end_front[1])%(2*len_knot) + 1, end_front[0]])
        else:
            knot.append([end_front[0], end_front[1], (end_front[0])%(2*len_knot) + 1, (end_front[1])%(2*len_knot) + 1])
    elif directions == "rl" or directions == "lr":
        if sign == "+":
            if right_dir_idx == 0: 
                knot.append([(end_front[0] - 2)%(2*len_knot) + 1,(end_front[1])%(2*len_knot) + 1, end_front[0], end_front[1]])
            else:
                knot.append([end_front[0], end_front[1], (end_front[0])%(2*len_knot) + 1, (end_front[1] - 2)%(2*len_knot) + 1])
        else:
            if right_dir_idx == 0: 
                knot.append([end_front[1], (end_front[0]-2)%(2*len_knot) + 1, (end_front[1])%(2*len_knot) + 1, end_front[0]])
            else:
                knot.append([(end_front[1]-2)%(2*len_knot) + 1, end_front[0], end_front[1], (end_front[0])%(2*len_knot) + 1])

    return canonical_representation(knot)

# For a knot, go through all crossings and attempt to apply a flype everywhere
def flype_list(knot:list[list[int]]):
    result = [knot]
    len_knot = len(knot)
    for crossing in knot:
        knot_1 = copy.deepcopy(knot)
        knot_1.remove(crossing)
        # Each crossing can be build out in four separate ways
        if (crossing[1] + 1)%(2*len_knot) == crossing[3]%(2*len_knot):
            flype_1 = apply_flype(copy.deepcopy(knot_1), [crossing[2], crossing[3]], [crossing[0], crossing[1]], "rr", "-")
            flype_2 = apply_flype(copy.deepcopy(knot_1), [crossing[1], crossing[2]], [crossing[0], crossing[3]], "rl", "-")
            flype_3 = apply_flype(copy.deepcopy(knot_1), [crossing[0], crossing[1]], [crossing[2], crossing[3]], "ll", "-")
            flype_4 = apply_flype(copy.deepcopy(knot_1), [crossing[3], crossing[0]], [crossing[1], crossing[2]], "lr", "-")
        else:
            flype_1 = apply_flype(copy.deepcopy(knot_1), [crossing[1], crossing[2]], [crossing[0], crossing[3]], "rr", "+")
            flype_2 = apply_flype(copy.deepcopy(knot_1), [crossing[0], crossing[1]], [crossing[2], crossing[3]], "rl", "+")
            flype_3 = apply_flype(copy.deepcopy(knot_1), [crossing[3], crossing[0]], [crossing[1], crossing[2]], "ll", "+")
            flype_4 = apply_flype(copy.deepcopy(knot_1), [crossing[2], crossing[3]], [crossing[0], crossing[1]], "lr", "+")

        # Only add the result if it isnt there already
        if flype_1 not in result and flype_1 != False:
            result.append(flype_1)
        if flype_2 not in result and flype_2 != False:
            result.append(flype_2)
        if flype_3 not in result and flype_3 != False:
            result.append(flype_3)
        if flype_4 not in result and flype_4 != False:
            result.append(flype_4)

    return result

# List of knots --> reduced list of knots such that the first element is not flype related to the others
def flype_reduce(knot_list: list[list[list[int]]]):
    unique_list = [knot_list[0]]

    max_depth = 5
    depth = 0
    all_flypes = [knot_list[0]]
    have_been_flyped = []
    while depth < max_depth:
        # Fill list of all flypes (of flypes) of the first knot
        for knot in all_flypes:
            # We dont want to do work twice
            if knot in have_been_flyped:
                continue
            have_been_flyped.append(knot)

            flyped = flype_list(knot)
            for flype_knot in flyped:
                if flype_knot in all_flypes:
                    continue
                all_flypes.append(flype_knot)
        # Delete knots in our original list if they are flype related to the first knot
        for knot_list_knot in knot_list:
            if knot_list_knot in all_flypes:
                knot_list.remove(knot_list_knot)
        # If all other knots from our original list are flype related to the first, we are done
        if len(knot_list) == 0:
            break
        depth += 1
    # Returns a list containing the first knot and all knots that are not flype related to it
    unique_list = unique_list + knot_list
    return unique_list

# 8.pass_reduced --> 9.jones_dict
# Creates a dict of the form {jones: [knots]}
# If not amphichiral, it writes either the knot or mirror image, not both
# Flype reduces the list of knots
def jones_dict_store():
    for i in range(3,11):
        file = open(f"8.pass_reduced/{i}.txt", "r")
        # create a dict:  {jones: [knots]}
        knot_dict = {}
        for line in file:
            knot = ast.literal_eval(line)     
            knot_jones = jones(knot)
            if knot_jones not in knot_dict:
                knot_dict[knot_jones] = [knot]
            else:
                knot_dict[knot_jones] = [knot] + knot_dict.get(knot_jones)

        file.close()

        print(len(knot_dict))

        knot_dict_2 = {}
        write_value = 0
        for key, value in knot_dict.items():
            # If mirror image is already in dict, skip it
            if key.subs(t, 1/t) in knot_dict_2:
                continue

            # Flype reduce
            if len(value) > 1:
                write_value = flype_reduce(value)
            else:
                write_value = value

            knot_dict_2[key] = write_value

        new_file = open(f"9.jones_dict/{i}", "ab")
        # "pickle" the dict into a binary file
        dump(knot_dict_2, new_file)
        new_file.close()

# Reads binary file and returns the dict stored there    
def jones_dict_load(i)-> dict:
    dbfile = open(f"9.jones_dict/{i}", 'rb')
    db = load(dbfile)
    dbfile.close()
    return db

# 9.jones_dict --> 10.theta_reduced
# Split values over multiple keys if they dont have the same Theta value
def split_by_theta():
    for i in range(3, 11):
        jones_dict = jones_dict_load(i)
        theta_reduced_dict = {}
        for key, value in jones_dict.items():
            # For 1 value, we dont need to compute theta
            if len(value) == 1:
                theta_reduced_dict[key] = value
                continue

            # Compute list of all theta values
            theta_list = []
            for knot in value:
                theta_list.append([theta(knot), knot])
            theta_list = sorted(theta_list)

            # Construct goupes for different Theta's
            groups = []
            current_group = [theta_list[0]]
            for val in theta_list[1:]:
                if abs(val[0] - current_group[-1][0]) < theta_bound:
                    current_group.append(val)
                else:
                    groups.append(current_group)
                    current_group = [val]

            groups.append(current_group)  

            # if 1 group, we dont need to split it
            if len(groups) == 1:
                theta_reduced_dict[key] = value
                continue

            # Check for mirror image
            seen_theta = [groups[0][0][0]]
            for group in groups[1:]:
                for seen_theta_value in seen_theta:
                    if abs(group[0][0] + seen_theta_value) < theta_bound:
                        groups.remove(group)
                        break
            
            # Remove Theta to have all values in dict have the same structure
            new_groups = []
            for group in groups:
                new_group = []
                for knot in group:
                    new_group.append(knot[1])
                new_groups.append(new_group)
                        
            # Create multiple entries from the groups
            j = 1
            for group in new_groups:
                theta_reduced_dict[(key, j)] = group
                j+=1
        
        new_file = open(f"10.theta_reduced/{i}", "ab")
        # "pickle" the dict into a binary file
        dump(theta_reduced_dict, new_file)
        new_file.close()
        
# Reads binary file and returns the dict stored there    
def theta_reduced_dict_load(i)-> dict:
    dbfile = open(f"10.theta_reduced/{i}", 'rb')
    db = load(dbfile)
    dbfile.close()
    return db
            
# Continously apply R3 and flypes
# Returns False if one of the knots is reducible
# Otherwise Returns a list such that te first element can not be found to be the same at the rest
def mixed_reduce(knot_list: list):
    unique_list = [knot_list[0]]

    max_depth = 10
    depth = 0
    all_applied_batch = [knot_list[0]]
    new_batch = []
    all_applied = []
    have_been_flyped_and_r3 = []
    while depth < max_depth:
        for knot in all_applied_batch:
            # Check if we have covered this knot already
            if knot in have_been_flyped_and_r3:
                continue
            have_been_flyped_and_r3.append(copy.deepcopy(knot))

            # Apply all R3s and flypes
            flyped = flype_list(copy.deepcopy(knot))
            r_3 = apply_R3(copy.deepcopy(knot))
            flyped_and_r3 = flyped + r_3
            # Check if reducable in crossing amount
            for f_r_knot in flyped_and_r3:
                if contains_trivial_R2(f_r_knot) or contains_R1(f_r_knot) or check_two_one_pass(f_r_knot):
                    return False
                
            # Dont append duplicates
            for knot_2 in flyped_and_r3:
                if knot_2 in all_applied:
                    continue
                new_batch.append(knot_2)
                all_applied.append(knot_2)
        
        for knot_list_knot in knot_list:
            if knot_list_knot in all_applied:
                knot_list.remove(knot_list_knot)
        
        # If we have reduced to 1 element (the one in unique_list)
        if len(knot_list) == 0:
            break

        all_applied_batch = new_batch
        new_batch = []

        depth += 1
    unique_list = unique_list + knot_list
    return unique_list

# 10.theta_reduced --> 11.mix_reduce
# applies the mixed_reduce algorithm to all sets of knot in the theta_reduced dict
def apply_mixed_reduce():
    for i in range(10, 11):
        knot_dict = theta_reduced_dict_load(i)
        new_dict = {}
        for key, value in knot_dict.items():
            new_value = mixed_reduce(copy.deepcopy(value))
            # if reducible, skip it
            if new_value == False:
                continue
            
            new_dict[key] = new_value
            
        new_file = open(f"11.mix_reduce/{i}", "ab")
        # "pickle" the dict into a binary file
        dump(new_dict, new_file)
        new_file.close()

# Reads binary file and returns the dict stored there    
def mix_reduced_dict_load(i)-> dict:
    dbfile = open(f"11.mix_reduce/{i}", 'rb')
    db = load(dbfile)
    dbfile.close()
    return db




def table_output(i):
    # Name & Figure & chiral & Jones & Theta($\pi, e$)\\\hline
    idx = 1
    chiral = ""
    knot_dict = mix_reduced_dict_load(i)
    for key, value in knot_dict.items():
        if type(key) == tuple:
            key = key[0]
        if key == key.subs(t, 1/t):
            knot = value[0]
            knot_fliped = copy.deepcopy(knot)
            for crossing in knot_fliped:
                # Flip the order
                crossing[1], crossing[3] = crossing[3], crossing[1]
                # Ensure that the Flip produces a valid PD code
                if (crossing[1]%(2*len(knot))) + 1 ==  crossing[3]:
                    crossing = crossing[1:] + crossing[:1]
                else: 
                    crossing = crossing[3:] + crossing[:3]
            if abs(theta(knot) - theta(knot_fliped)) < theta_bound:
                chiral = "yes"
            else:
                chiral = "no"
        else:
            chiral = "no"

        split_jones = split_expression(key)
        if len(split_jones) == 1:
            jones_output = f"${latex(split_jones[0])}$"
        else:
            # \makecell{$- t^{12} + t^{11} - 2 t^{10} + 3 t^{9} - 3 t^{8}$ \\ $+3t^{7} - 2 t^{6} + 2 t^{5} - t^{4} + t^{3}$}
            jones_output = f"\makecell\u007b ${latex(split_jones[0])}$ \\\\ ${latex(split_jones[1])}$  \u007d"
        
        print(f"${i}_\u007b{idx}\u007d$ & \includegraphics[height = 2cm]\u007b knots/{i}_{idx}.png\u007d & {chiral} & {jones_output} & {format(float(theta(value[0])),'.8f')}\\\\\hline")
        idx+=1

def pd_check(knot):
    tally = [0 for _ in range(2*len(knot))]
    for crossing in knot:
        for number in crossing:
            tally[number - 1] += 1
    for number in tally:
        if number != 2:
            return False
    return True

def pd_check_knots(knot_list):
    for knot in knot_list:
        if pd_check(knot):
            continue
        else:
            print(f"non-valid knot: {knot}")

def count_entries():
    count_list = []
    for i in range(3, 11):
        file = open(f"8.pass_reduced/{i}.txt", "r")
        count = 0
        for line in file:
            count +=1
        count_list.append([i, count])
    print(count_list)
    
def split_expression(expr, max_terms=8):
    # Simplify and get individual terms
    # expr = simplify(expr)
    terms = expr.as_ordered_terms()

    n = len(terms)
    if n <= max_terms:
        return [expr]  # No need to split
    
    # Split the terms into chunks
    
    mid = n // 2
    expr1 = Add(*terms[:mid+1])
    expr2 = Add(*terms[mid+1:])

    return [expr1, expr2]


if __name__ == "__main__":
    # 1.Plantri_Data --> 2.Plantri_knots
    print_knots()

    # 2.Plantri_knots --> 3.Plantri_knots_with_sign
    add_sign_to_crossing()

    # 3.Plantri_knots_with_sign --> 4.PD_knots
    PD_knots()

    # 4.PD_knots --> 5.PD_No_R2
    remove_trivial_R2()

    # 5.PD_No_R2 --> 6.Reduced_knots
    reduce_knots_by_R3()

    # 6.Reduced_knots --> 7.no_dupes
    remove_duplicates()

    # 7.no_dupes --> 8.pass_reduced
    reduce_by_pass()

    # 8.pass_reduced --> 9.jones_dict
    jones_dict_store()

    # 9.jones_dict --> 10.theta_reduced
    split_by_theta()

    # 10.theta_reduced --> 11.mix_reduce
    apply_mixed_reduce()
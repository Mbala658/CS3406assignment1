# CS4306 Assignment 1
# Author: Josue Rojo
# 20 June 2026

"""
Pseudocode:

Start with every hospital having no matched residents.
Start with every resident having no matched hospital.
Keep track of the next resident each hospital will ask.

While there is a hospital with open slots and residents left to ask:
    Pick that hospital.
    Pick the next resident from that hospital's preference list.
    If the resident is not in the resident list:
        Skip that resident.
    If the resident does not list that hospital:
        Skip that proposal.
    If the resident is unmatched:
        Match the resident to that hospital.
    Else:
        Compare the resident's current hospital with the new hospital.
        If the resident likes the new hospital more:
            Remove the resident from the old hospital.
            Match the resident to the new hospital.
        Else:
            Keep the old match.

After the matching is done:
    Check if the matching is stable.
    If stable, print the hospital matches.
"""

import sys

RANK_NOT_FOUND = 10 ** 100  # fallback rank for not listed / not acceptable


def read_input_file(file_name):
    
    hospitals = {}  # all hospital records
    
    residents = {}  # all resident records

    reading_hospitals = True  # input contract: hospitals come before blank line

    input_file = open(file_name, "r")  # open input file for reading

    for line in input_file:
        
        line = line.strip()  # remove outside spaces and newline

        if line == "":  # blank line means hospital section is done
            reading_hospitals = False
            continue

        line_parts = line.split(",")  # split comma separated values

        for index in range(len(line_parts)):  # clean each value after split
            line_parts[index] = line_parts[index].strip()

        if reading_hospitals == True:
            
            hospital_name = line_parts[0]  # hospital name from first value
            
            slot_count = int(line_parts[1])  # number of positions at hospital
            
            hospital_preference_list = line_parts[2:]  # residents ranked by this hospital

            hospitals[hospital_name] = {}  # make hospital record
            
            hospitals[hospital_name]["slots"] = slot_count  # store hospital capacity
            
            hospitals[hospital_name]["preferences"] = hospital_preference_list  # store hospital ranking

        else:
            resident_name = line_parts[0]  # resident name from first value
            
            resident_preference_list = line_parts[1:]  # hospitals ranked by this resident

            residents[resident_name] = {}  # make resident record
            
            residents[resident_name]["preferences"] = resident_preference_list  # store resident ranking

    input_file.close()  # close input file

    return hospitals, residents  # output contract: two dictionaries


def find_rank(preference_list, name_to_find):
    
    # finds where a name is in a preference list
    # smaller number means higher rank / more liked

    if name_to_find in preference_list:
        return preference_list.index(name_to_find)

    return RANK_NOT_FOUND  # not found means treated like bottom rank


def resident_prefers_hospital(residents, resident_name, new_hospital_name, current_hospital_name):
    
    # checks if resident likes new hospital over current hospital

    preference_list = residents[resident_name]["preferences"]  # get this resident ranking

    new_hospital_rank = find_rank(preference_list, new_hospital_name)  # rank of new hospital
    
    current_hospital_rank = find_rank(preference_list, current_hospital_name)  # rank of current hospital

    if new_hospital_rank < current_hospital_rank:  # lower rank number means better choice
        return True

    return False


def hospital_prefers_resident(hospitals, hospital_name, new_resident_name, current_resident_name):
    
    # checks if hospital likes new resident over current resident

    preference_list = hospitals[hospital_name]["preferences"]  # get this hospital ranking

    new_resident_rank = find_rank(preference_list, new_resident_name)  # rank of new resident
    
    current_resident_rank = find_rank(preference_list, current_resident_name)  # rank of current resident

    if new_resident_rank < current_resident_rank:  # lower rank number means better choice
        return True

    return False


def modified_gale_shapley(hospitals, residents):
    
    hospital_matches = {}  # hospital name to list of matched residents
    
    resident_matches = {}  # resident name to matched hospital
    
    next_proposal_index = {}  # next resident each hospital will propose to

    for hospital_name in hospitals:
        
        hospital_matches[hospital_name] = []  # hospital starts with no residents 
        
        next_proposal_index[hospital_name] = 0  # hospital starts at first resident in its list

    for resident_name in residents:
        
        resident_matches[resident_name] = None  # resident starts unmatched  
    
    while True:
        proposing_hospital = None  # no hospital selected yet  

        # find first hospital that has room and has someone left to propose to
        
        for hospital_name in hospitals:
            
            has_open_slot = len(hospital_matches[hospital_name]) < hospitals[hospital_name]["slots"]  # capacity check
            
            has_resident_left = next_proposal_index[hospital_name] < len(hospitals[hospital_name]["preferences"])  # proposal list check

            if has_open_slot == True and has_resident_left == True:
                
                proposing_hospital = hospital_name  # this hospital can make next proposal
                break

        if proposing_hospital == None:  # loop contract: stop when no hospital can propose
            break

        hospital_preference_list = hospitals[proposing_hospital]["preferences"]  # hospital ranking list

        proposed_resident = hospital_preference_list[next_proposal_index[proposing_hospital]]  # next resident to ask
        
        next_proposal_index[proposing_hospital] = next_proposal_index[proposing_hospital] + 1  # move hospital pointer forward

        if proposed_resident not in residents:  # resident name not in resident section
            continue

        if proposing_hospital not in residents[proposed_resident]["preferences"]:  # resident does not accept this hospital
            continue

        current_hospital = resident_matches[proposed_resident]  # resident current match

        if current_hospital == None:
            hospital_matches[proposing_hospital].append(proposed_resident)  # put resident at proposing hospital
            
            resident_matches[proposed_resident] = proposing_hospital  # update resident match

        else:
            if resident_prefers_hospital(residents, proposed_resident, proposing_hospital, current_hospital) == True:
                
                hospital_matches[current_hospital].remove(proposed_resident)  # remove resident from old hospital
                
                hospital_matches[proposing_hospital].append(proposed_resident)  # add resident to new hospital
                
                resident_matches[proposed_resident] = proposing_hospital  # update resident to new hospital

            else:
                pass  # resident rejects proposal, so no match changes

    return hospital_matches, resident_matches  # output contract: matching both ways


def check_stability(hospitals, residents, hospital_matches, resident_matches):
    
    # first contract check: no hospital can have more residents than slots

    for hospital_name in hospitals:
        if len(hospital_matches[hospital_name]) > hospitals[hospital_name]["slots"]:  # hospital over capacity
            return False

    # second contract check: current matches must be acceptable and agree both ways
    for hospital_name in hospital_matches:
        
        for resident_name in hospital_matches[hospital_name]:
            
            if resident_name not in hospitals[hospital_name]["preferences"]:  # hospital did not rank this resident
                return False

            if hospital_name not in residents[resident_name]["preferences"]:  # resident did not rank this hospital
                return False

            if resident_matches[resident_name] != hospital_name:  # hospital side and resident side disagree
                return False

    # stability check: look for pair where both sides would rather be together

    for hospital_name in hospitals:
        
        for resident_name in residents:
            
            if resident_matches[resident_name] == hospital_name:  # already matched together
                continue

            if resident_name not in hospitals[hospital_name]["preferences"]:  # hospital does not accept resident
                continue

            if hospital_name not in residents[resident_name]["preferences"]:  # resident does not accept hospital
                continue

            current_hospital = resident_matches[resident_name]  # resident current hospital

            if current_hospital == None:
                resident_wants_hospital = True  # unmatched resident wants acceptable hospital
                
            else:
                resident_wants_hospital = resident_prefers_hospital(residents, resident_name, hospital_name, current_hospital)  # compare hospital choices

            hospital_has_open_slot = len(hospital_matches[hospital_name]) < hospitals[hospital_name]["slots"]  # hospital capacity check

            if hospital_has_open_slot == True:
                
                hospital_wants_resident = True  # open slot means hospital can take acceptable resident
                
            else:
                hospital_wants_resident = False  # no open slot, so must beat someone current

                for current_resident in hospital_matches[hospital_name]:
                    
                    if hospital_prefers_resident(hospitals, hospital_name, resident_name, current_resident) == True:
                        
                        hospital_wants_resident = True  # hospital likes outside resident more than current resident
                        
                        break

            if resident_wants_hospital == True and hospital_wants_resident == True:
                return False  # blocking pair found, not stable

    return True  # no blocking pair found


def print_matches(hospital_matches):
    
    # prints each hospital followed by assigned residents

    for hospital_name in hospital_matches:
        
        print(hospital_name, end="")  # print hospital first

        for resident_name in hospital_matches[hospital_name]:
            
            print(", " + resident_name, end="")  # print one assigned resident

        print()  # finish this hospital line


def main():
    # use command line file if given
    # otherwise use sample file name

    if len(sys.argv) > 1:
        input_file = sys.argv[1]  # file typed after python command
    else:
        input_file = "sample_input_1.txt"  # default test file

    hospitals, residents = read_input_file(input_file)  # read and store input

    hospital_matches, resident_matches = modified_gale_shapley(hospitals, residents)  # run matching algorithm

    stable = check_stability(hospitals, residents, hospital_matches, resident_matches)  # verify stability

    if stable == True:
        print_matches(hospital_matches)  # print only matching, assignment format
        
    else:
        print("The matching is not stable.")  # only show this if stability check fails
        print_matches(hospital_matches)  # still show produced matching


main()
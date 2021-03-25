'''
# add outside border -> detect more table (less 4 joint table)
# start : 20200301
# update : 20200301
# minku Koo
'''

# if table has no outside border
# this function can make virtual border line around table
def addOutline(direction, mask, contours, line_size = 2):
    """
    Parameters
    ----------
        direction <str> : "v" or "h" (vertical or horizontal), line direction
        mask <numpy nd.array> : Threshold (image binary array) 
        contours <tuple in list> : table area coordinates list like [(x, y, w, h), ... ]
        line_size <int> : outside border line size (default = 2)
    
    return 
    ----------
        mask <numpy nd.array> : make virture outside border line on table 
    """
    for c in contours:
        x, y, w, h = c
        
        if direction=="v": # if vertical line
            mask[ y : y+h ,x-line_size : x+line_size ]= 255
            mask[ y : y+h ,x+w-line_size : x+w+line_size ]= 255 
        elif direction=="h": # if horizontal line
            mask[ y+h-line_size : y+h+line_size, x : x+w ]= 255
            mask[ y-line_size : y+line_size, x : x+w ]= 255
    
    return mask

if __name__ ==  "__main__":
    print("I AM MAKE_BORDER MAIN")
    '''
    # How to use?
    
    from make_border import addOutline # call module
    
    # vertical and horizontal mask are made from find_lines()
    contours = find_contours(vertical_mask, horizontal_mask) # method in parser.Lattice() 
    
    vertical_mask = addOutline("v", vertical_mask, contours)
    horizontal_mask = addOutline("h", horizontal_mask, contours)
    
    '''


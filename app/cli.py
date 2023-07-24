from argparse import ArgumentParser
import os
import sys
import hashlib
from collections import defaultdict as dd

line = 0
line_count = 24
stretch_fn = 32

def subtract_keys_dicts(d1, d2):
    #d1 "-" d2, subtract boolean operation
    return {key : d1[key] for key in d1.keys() if key not in d2}

def union_keys_dicts(d1, d2):
    return {key : d1[key] for key in d1.keys() if key in d2}

def exclude_vals_dicts(d1, d2):
    return {key : d1[key] for key in d1.keys() if key in d2 and d1[key] != d2[key]}

def exclude_two_sets(s1, s2):
    #Copy set to avoid modifying while iterating
    ls1 = list(s1)
    for key in ls1:
        if key in s2:
            s1.remove(key)
            s2.remove(key)

def exclude_two_sets_count(s1, s2, count):
    #Copy set to avoid modifying while iterating
    ls1 = list(s1)
    for key in ls1:
        if key in s2 and count > 0:
            s1.remove(key)
            s2.remove(key)
            count -= 1

def try_stretch_fn(fn):
    return fn + " " * (stretch_fn - len(fn))

def println(msg):
    print(msg)
    global line
    line += 1
    if line >= line_count:
        line = 0
        input("[Press Enter for more]")

def main():
    #Load args
    parser = ArgumentParser(prog='cli')
    parser.add_argument('dir_a', help="baseline comparison folder")
    parser.add_argument('dir_b', help="comparing folder")
    parser.add_argument("--line_count", default=24, required = False, dest = "LINE_COUNT", help="number of lines to println in one console window")
    args = parser.parse_args()
    global line_count
    line_count = int(args.LINE_COUNT)

    #More setup
    println("Initializing folder diff with folders [{0}] and [{1}]".format(args.dir_a, args.dir_b))
    cwd = os.getcwd()
    dira = os.path.join(cwd, args.dir_a)
    dirb = os.path.join(cwd, args.dir_b)
    uniquefola = dira[len(os.path.commonpath([dira, dirb])):]
    uniquefolb = dirb[len(os.path.commonpath([dira, dirb])):]

    dira_dict = {}
    dirb_dict = {}
    rev_dira_dict = dd(set)
    rev_dirb_dict = dd(set)

    #Hashes first folder
    println("")
    println("For Folder A: " + uniquefola  + ": ")
    println("--------")
    for filename in os.listdir(dira):
        f = os.path.join(dira, filename)
        # checking if it is a file
        if os.path.isfile(f):
            # println("File: {0}".format(f))
            BUF_SIZE = 32768 # Read file in 32kb chunks
            md5 = hashlib.md5()
            with open(f, 'rb') as F:
                while True:
                    data = F.read(BUF_SIZE)
                    if not data:
                        break
                    md5.update(data)
                println("MD5 for {0}: {1}".format(try_stretch_fn(filename), md5.hexdigest()))
                dira_dict[filename] = md5.hexdigest()
                rev_dira_dict[md5.hexdigest()].add(filename)
    println("")

    #Hashes second folder
    println("For Folder B: " + uniquefolb + ": ")
    println("--------")
    for filename in os.listdir(dirb):
        f = os.path.join(dirb, filename)
        # checking if it is a file
        if os.path.isfile(f):
            # println("File: {0}".format(f))
            BUF_SIZE = 32768 # Read file in 32kb chunks
            md5 = hashlib.md5()
            with open(f, 'rb') as F:
                while True:
                    data = F.read(BUF_SIZE)
                    if not data:
                        break
                    md5.update(data)
                hex = md5.hexdigest()
                println("MD5 for {0}: {1}".format(try_stretch_fn(filename), hex))
                dirb_dict[filename] = md5.hexdigest()
                rev_dirb_dict[hex].add(filename)

    #Start diff
    dirb_exc_dict = subtract_keys_dicts(dirb_dict, dira_dict)
    dira_exc_dict = subtract_keys_dicts(dira_dict, dirb_dict)
    dirb_exc_msg_dict = {}
    dira_exc_msg_dict = {}
    diff_dict  = exclude_vals_dicts(dira_dict, dirb_dict)
    match_hash_dict = union_keys_dicts(rev_dira_dict, rev_dirb_dict)

    println("")
    println("Diff: ")
    println("--------")
    # Determines extra specifying messages for differences, and printlns our file equalities (likely renames) which filter out files that are equal in name
    toPrintHeader = True #Only print the header for this section if it's gonna print something
    for k in match_hash_dict:
        a_fn_set = rev_dira_dict[k]
        b_fn_set = rev_dirb_dict[k]
        msg = ""
        if len(a_fn_set) != len(b_fn_set):
            exclude_two_sets_count(a_fn_set, b_fn_set, min(len(a_fn_set), len(b_fn_set)) - 1)
        else:
            temp_alen = len(a_fn_set)
            exclude_two_sets(a_fn_set, b_fn_set)
            if len(a_fn_set) != temp_alen:
                msg = " (which also match other files in both folders)"
        a_fn_set_single = len(a_fn_set) == 1
        b_fn_set_single = len(b_fn_set) == 1
        if len(a_fn_set) == 0 and len(b_fn_set) == 0:
            continue
        if len(a_fn_set) == 0 or  len(b_fn_set) == 0:
            raise Exception("Internal Error")
        arga = "{0} [A] is".format(list(a_fn_set)[0]) if a_fn_set_single else "files with same MD5 hash {0} [A] are".format(a_fn_set)
        argb = "{0} [B]"   .format(list(b_fn_set)[0]) if b_fn_set_single else "files with same MD5 hash {0} [B]"    .format(b_fn_set)
        if toPrintHeader:
            println("Renames/Copies: ")
            toPrintHeader = False
        println("{0} equal to {1}{2}".format(arga, argb, msg))
        for fn in a_fn_set:
            dira_exc_msg_dict[fn] = " (but {0} contents there)".format("{0} matches".format(list(b_fn_set)[0]) if b_fn_set_single else "multiple files in folder B match")
        for fn in b_fn_set:
            dirb_exc_msg_dict[fn] = " (but {0} contents there)".format("{0} matches".format(list(a_fn_set)[0]) if a_fn_set_single else "multiple files in folder A match")
    if toPrintHeader == False:
        println("")

    #Prints out differences
    if len(diff_dict) != 0:
        println("Changes: ")
        for key in diff_dict:
            println("{0} differs".format(key))
        println("")

    if len(dira_exc_dict) != 0 or len(dirb_exc_dict) != 0:
        println("Different Files: ")
        for key in dira_exc_dict:
            println("{0} does not exist in Folder B".format(try_stretch_fn(key)) + (dira_exc_msg_dict[key] if key in dira_exc_msg_dict else ""))
        for key in dirb_exc_dict:
            println("{0} does not exist in Folder A".format(try_stretch_fn(key)) + (dirb_exc_msg_dict[key] if key in dirb_exc_msg_dict else ""))
        println("")




if __name__ == '__main__':
    main()


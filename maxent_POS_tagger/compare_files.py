#!/usr/bin/env python3
def compare_files(f1, f2):
    with open(f1, 'r') as file1, open(f2, 'r') as file2:
        lines1 = list(map(lambda s: s.strip(), file1.readlines()))
        lines2 = list(map(lambda s: s.strip(), file2.readlines()))
    for l1, l2 in zip(lines1, lines2):
        s1 = {_ for _ in l1.split()}
        s2 = {_ for _ in l2.split()}
        if s1 != s2:
            print("mine: {0}\ngold: {1}".format(l1, l2))
            print("Difference: {0}".format(s2.difference(s1)))
if __name__ == "__main__":
    compare_files("res_5_10/final_train.vectors.txt", "examples/ex_final_train.vectors.txt")
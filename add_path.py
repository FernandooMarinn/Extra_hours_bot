import sys
import os


def add_path():
    current_folder = os.path.abspath(os.getcwd())
    parent_folder = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    sys.path.append(current_folder)
    sys.path.append(parent_folder)



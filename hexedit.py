import curses
import os
import argparse
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import pathlib
import math
from properties import *

curr_file_name = ""


def print_resize_message(my_screen):
    my_screen.addstr(0, 0, "Please, resize your term to 125 , 40 pixels")
    my_screen.refresh()


def divide_file(args) -> int:
    file_size = os.path.getsize(args.file)
    pages_amount = file_size // 624 + 1
    with open(args.file, 'rb') as f:
        inner_page_counter = 0
        while True:
            chunk = f.read(624)
            if len(chunk) == 0:
                return inner_page_counter
            with open(args.file+str(inner_page_counter)+".temp", "wb") as tmp:
                tmp.write(chunk)
            inner_page_counter += 1
    return pages_amount


def build_dump(filename, current_page):
    full_path = filename + str(current_page) + ".temp"
    offset = 0
    chunks = []

    with open(full_path, 'rb') as f:
        while True:
            chunk = f.read(16)
            if len(chunk) == 0:
                break
            text = str(chunk)
            text = ''.join([i if 128 > ord(i) > 32
                            else "." for i in text])
            output = "{:#08x}".format(offset) + ": "
            output += " ".join("{:02X}".format(c)
                               for c in chunk[:8])
            output += " | "
            output += " ".join("{:02X}".format(c)
                               for c in chunk[8:])
            if len(chunk) % 16 != 0:
                output += "   " * (16 - len(chunk)) + text
            else:
                output += " " + text
            chunks.append(output)
            offset += 16
    return chunks


def save_page_dump(my_screen, current_page, args, chunk_len):
    current_page_path = args.file + str(current_page) + ".temp"
    fin = ""
    chrc = None
    for i in range(chunk_len):
        for j in PROPER_POSITIONS:
            chrc = ord(my_screen.instr(i, j, 1))
            if chrc == 32 or chrc == ord("|"):
                break
            character = my_screen.instr(i, j, 1).decode('utf-8')[0]
            fin += character
    try:
        parsed_line = bytearray.fromhex(fin).decode()
    except ValueError:
        print("Cought error")
    with open(current_page_path, "w", newline='') as edited_file:
        edited_file.write(parsed_line)


def save_full_dump(my_screen, current_page, pages_amount, args, chunk_len):
    current_page_path = args.file + str(current_page) + ".temp"
    fin = ""
    chrc = None
    for i in range(chunk_len):
        for j in PROPER_POSITIONS:
            chrc = ord(my_screen.instr(i, j, 1))
            if chrc == 32 or chrc == ord("|"):
                break
            character = my_screen.instr(i, j, 1).decode('utf-8')[0]
            fin += character
    try:
        parsed_line = bytearray.fromhex(fin).decode()
    except ValueError:
        print("Cought error")
    with open(current_page_path, "w", newline='') as edited_file:
        edited_file.write(parsed_line)
    with open("edited_" + args.file, "a") as final_edited:
        for i in range(pages_amount):
            page_path = args.file + str(i) + ".temp"
            with open(page_path, 'r') as tmp:
                page = tmp.readlines()
                final_edited.write("".join(page))
            os.remove(page_path)


def wait_for_proper_char(my_screen):
    proper = False
    while not proper:
        new_character = my_screen.getch()
        new_character = chr(new_character).capitalize()
        if new_character in PROPER_NUMBERS_HEX:
            proper = True
    return new_character


def print_page(args, current_page, my_screen):
    my_screen.erase()
    act_chunks = build_dump(args.file, current_page)
    my_screen.attron(curses.color_pair(1))
    i = 0
    for chunk in act_chunks:
        my_screen.addstr(i, 1, chunk)
        i += 1
    my_screen.attroff(curses.color_pair(1))


def show_menu(my_screen, args, pages_amount):
    my_screen.erase()
    if os.name == 'posix':
        h, w = my_screen.getmaxyx()
        while h != 40 or w != 125:
            print_resize_message(my_screen)
            h, w = my_screen.getmaxyx()
    else:
        curses.resize_term(40, 125)
        h, w = my_screen.getmaxyx()
    my_screen.erase()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    my_screen.attron(curses.color_pair(1))
    current_page = 0
    act_chunks = build_dump(args.file, current_page)
    i = 0
    for chunk in act_chunks:
        my_screen.addstr(i, 1, chunk)
        i += 1
    my_screen.attroff(curses.color_pair(1))
    h, w = my_screen.getmaxyx()
    i = 0
    while True:
        key = my_screen.getch()
        cursor_pos_x, cursor_pos_y = my_screen.getyx()
        if key == KEY_UP:
            cursor_pos_x -= 1

        elif key == KEY_DOWN:
            cursor_pos_x += 1

        elif key == KEY_RIGHT:
            i += 1
            if i >= len(PROPER_POSITIONS):
                i = 0
            cursor_pos_y = PROPER_POSITIONS[i]

        elif key == KEY_LEFT:
            i -= 1
            if i < 0:
                i = len(PROPER_POSITIONS) - 1
            cursor_pos_y = PROPER_POSITIONS[i]

        elif key == ord("q"):
            save_full_dump(my_screen,
                           current_page,
                           pages_amount,
                           args,
                           len(act_chunks))
            break

        elif key == 10:
            new_character = wait_for_proper_char(my_screen)
            my_screen.addch(cursor_pos_x, cursor_pos_y, new_character)
            full_hex_line_beg = my_screen.instr(cursor_pos_x, 11, 23)
            full_hex_line_end = my_screen.instr(cursor_pos_x, 37, 23)
            full_hex = full_hex_line_beg + bytes(" ", "utf8") \
                + full_hex_line_end
            str_temp = full_hex.decode("utf8")
            new_dump = bytearray.fromhex(str_temp).decode()
            decoded_hex = ''.join([i if 128 > ord(i) > 32 or
                                   ord(i) == 10 or ord(i) == 13
                                   else "." for i in new_dump])
            check_str = '' + str(bytes(decoded_hex, 'utf8'))
            my_screen.addnstr(cursor_pos_x, 61, check_str, len(check_str))

        elif key == ord("s"):
            save_full_dump(my_screen,
                           current_page,
                           pages_amount,
                           args,
                           len(act_chunks))

        elif key == 339:  # pageUp
            save_page_dump(my_screen, current_page, args, len(act_chunks))
            current_page += 1
            if current_page >= pages_amount:
                current_page = 0
            print_page(args, current_page, my_screen)
            i = 0

        elif key == 338:  # page down
            save_page_dump(my_screen, current_page, args, len(act_chunks))
            current_page -= 1
            if current_page < 0:
                current_page = pages_amount - 1
            print_page(args, current_page, my_screen)
            i = 0

        if cursor_pos_x >= h - 1 or cursor_pos_x < 0:
            cursor_pos_x = 0

        character = my_screen.instr(cursor_pos_x, cursor_pos_y, 1)
        character = character.decode('utf-8')[0]
        my_screen.addstr(h - 1, 0, f"You selected :{character}")
        my_screen.move(cursor_pos_x, cursor_pos_y)
        my_screen.refresh()


def main():
    global curr_file_name
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Specify a filepath")
    parser.add_argument('-o', '--output',
                        help="Print output to a terminal",
                        action="store_true")
    args = parser.parse_args()
    current_directory = pathlib.Path('.')
    if args.file:
        curr_file_name = current_directory.joinpath("edited_" +
                                                    args.file).absolute()
        pages_amount = divide_file(args)
        curses.wrapper(show_menu, args, pages_amount)
    else:
        print(parser.usage)

if __name__ == '__main__':
    main()

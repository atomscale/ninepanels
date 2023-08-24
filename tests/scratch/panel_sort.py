from pprint import PrettyPrinter

pp = PrettyPrinter()


db_sorted = [
    {"id": 20, "position": 0},
    {"id": 30, "position": 1},
    {"id": 10, "position": 2},
    {"id": 80, "position": 3},
    {"id": 70, "position": 4},
    {"id": 73, "position": 5},
    {"id": 74, "position": 6},
    {"id": 888, "position": 7},
    {"id": 13, "position": 8},
]

pp.pprint(db_sorted)
print()

max_pos = len(db_sorted) - 1
min_pos = 0

incoming_update = {"id": 888, "position": 2}
new_pos = incoming_update['position']

for i, panel in enumerate(db_sorted):
    if panel['id'] == incoming_update['id']:
        focus_panel = panel # essentially saved to memeory
        focus_panel_cur_index = i


cur_pos = focus_panel['position']

if not new_pos == cur_pos and new_pos <= max_pos and new_pos >= min_pos:

    # will need to remove the focus_panel for now if not do nothing:
    db_sorted.pop(focus_panel_cur_index)
    pp.pprint(db_sorted)
    print()

    if new_pos < cur_pos:
        # everythign below the cur pos until the new_pos must be incremenete dby one
        for panel in db_sorted:
            if panel['position'] < cur_pos and panel['position'] >= new_pos:
                panel['position'] = panel['position'] + 1

    if new_pos > cur_pos:
        # everythign above the cur pos until the new_pos must be decremenete dby one
        for panel in db_sorted:
            if panel['position'] > cur_pos and panel['position'] <= new_pos:
                panel['position'] = panel['position'] - 1
                # db commit here

    pp.pprint(db_sorted)
    print()
    # amend the focus panel item with the new required postion:
    focus_panel['position'] = new_pos
    # insert back the focus_panel:=, use the fact pos is the same as index inthe sorted db output
    db_sorted.insert(new_pos, focus_panel)

    pp.pprint(db_sorted)
else:
    print("do nothing")








# -*- coding: utf-8 -*-

# DATA
import geopandas as gpd
import pandas as pd

# GUI
import tkinter as tk
from tkinter import (
    scrolledtext,
    filedialog,
    ttk,
    messagebox,
    Button,
    Label,
    Scrollbar,
    Frame,
    Canvas,
)

# BASIC
import math
import re
import os
import sys
import random
from datetime import datetime
import pathlib

# GLOBAL VARIABLES
global data, standard, input_file, columns_mapped, is_populated

data = None
standard = None
input_file = None
is_populated = False


def control_date(date_text):
    try:
        res = datetime.strptime(date_text, "%Y-%m-%d")  # ISO 8601
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res


def control_date_alt1(date_text):
    try:
        res = datetime.strptime(date_text, "%d-%m-%Y")
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res


def control_date_alt2(date_text):
    try:
        res = datetime.strptime(date_text, "%y-%m-%d")
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res


def control_datetime(datetime_text):
    try:
        res = datetime.strptime(datetime_text, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res


def control_time(time_ext):
    try:
        res = datetime.strptime(time_ext, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # ~ raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return None
    return res


def write_log(files, columns, log):
    """
    Write log of transforming file
    - Date and time
    - Input data and Data Schema name
    - Correspondence between Data Schema and Input Data Fields
    """

    f = open(log, "w+")

    # Ecriture de la date #########################
    # dd/mm/YY H:M:S
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    l = "Date and time : %s\n" % dt_string
    f.write(l)
    l = "------------------------\n"
    f.write(l)

    # Ecriture du fichier source et du standard de destination #########################

    input_file = files[0]
    output_file = files[1]
    standard_file = files[2]
    output_mapping = files[3]

    l = ("Input data : %s\n") % (os.path.basename(input_file))
    f.write(l)
    l = ("Input data Path : %s\n") % (input_file)
    f.write(l)
    l = ("Data schema : %s\n") % (os.path.basename(standard_file))
    f.write(l)
    l = ("Data schema Path : %s\n") % (standard_file)
    f.write(l)
    l = ("Data mapping : %s\n") % (os.path.basename(output_mapping))
    f.write(l)
    l = ("Data mapping Path : %s\n") % (output_mapping)
    f.write(l)
    l = ("Output data : %s\n") % (os.path.basename(output_file))
    f.write(l)
    l = ("Output data Path : %s\n") % (output_file)
    f.write(l)

    l = "------------------------\n"
    f.write(l)

    # Data Schema

    l = "[SCHEMA]\n"
    f.write(l)

    standard_fields = columns[0]
    standard_descriptions = columns[1]

    for i, elt in enumerate(standard_fields):
        l = ("%s : %s\n") % (elt, standard_descriptions[i])
        f.write(l)
    l = "------------------------\n"
    f.write(l)

    # Data Schema conformance #########################

    l = "[SCHEMA <- DATA]\n"
    f.write(l)

    columns_mapped = columns[2]

    for i, elt in enumerate(standard_fields):
        standard_field = standard_fields[i]
        if standard_field in columns_mapped:
            lib_source_column = str(
                list(data.columns)[columns_mapped.index(standard_field)]
            )
        else:
            lib_source_column = "__"
        l = ("%s <- %s\n") % (standard_field, lib_source_column)
        f.write(l)

    l = "------------------------\n"
    f.write(l)

    # Data Transformation #########################

    l = "[DATA -> SCHEMA]\n"
    f.write(l)
    for i, elt in enumerate(list(data.columns)):
        if elt not in ("geom", "geometry"):
            data_colonne = elt
            column_mapped = columns_mapped[i]
            l = ("%s -> %s\n") % (
                data_colonne,
                column_mapped if column_mapped is not None else "__",
            )
            f.write(l)

    f.close()


def populate_source_target(frame, data=None, standard=None):
    """
    Function that populates the right panel
    with the source and target columns to match
    """

    global is_populated

    if data is not None:
        data_colonnes = list(data.columns)

    if standard is not None:
        standard_colonnes = list(standard.iloc[:, 0])

    # Block with combo boxes
    # correspond to standard values
    global combos, labels, labels_control

    # Remove elements from the populated panel
    if is_populated is True:
        for elt in combos:
            elt.destroy()
        for elt in labels:
            elt.destroy()

    data_colonnes = list(data.columns)
    combos = list()
    labels = list()
    labels_control = list()
    for row, elt in enumerate(data_colonnes):
        if (
            elt != "geometry"
        ):  # we don't allow renaming of geometry columns, when data is spatial (gpkg or shp)

            # 1 - Labels
            # Text with the source variable name
            label = Label(rightframe, text="%s" % elt, bg="white")
            label.grid(row=row, column=0)
            labels.append(label)

            # 2 - Comboboxes
            # If standard file/data is specified
            # then we add the standard columns comboboxes
            # the user will choose in the lists/combos which target column corresponds to each source column
            if standard is not None:
                combo = ttk.Combobox(rightframe)
                combo["values"] = ["_%s" % elt] + standard_colonnes

                # Default position on equivalent source column
                # when source column (data) = standard data column (destination)
                i = [i for i, elt2 in enumerate(combo["values"]) if elt == elt2]
                if len(i) > 0:
                    combo.current(
                        i[0]
                    )  # we position the list on the corresponding item
                else:
                    combo.current(0)
                combo.grid(row=row, column=1)

                combos.append(
                    combo
                )  # we add the combo to the list of combos. combos will help when renaming data

                # 3 - Labels for controlling
                label_control = Label(
                    rightframe, text="Press 'Check' to control the type", bg="white"
                )
                label_control.grid(row=row, column=2)
                labels_control.append(label_control)

        is_populated = True


def onFrameConfigure(canvas):

    canvas.configure(scrollregion=canvas.bbox("all"))


def print_data(data):
    """
    Displays data information in the data information box
    """

    rows = list()
    data_colonnes = list(data.columns)

    for i in range((data.shape[1] - 1)):
        a = data.iloc[:, i].unique()
        if a.dtype == "int64":
            elts = [
                "NA" if elt is None else str(elt) for elt in list(a)
            ]  # 'NA' if None
        elif a.dtype == "bool":
            elts = ["TRUE" if elt == True else "FALSE" for elt in list(a)]
        else:
            elts = ["NA" if elt is None else elt for elt in list(a)]

        # We randomly select 10 elements
        # if there are more than 9 unique items
        if len(elts) > 9:
            elts = random.sample(elts, 10)

        # Conversion in String
        elts = [str(elt) for elt in elts]

        v = ",".join(elts)
        v = data_colonnes[i] + " : " + v
        rows.append(v)

    v = "\n".join(rows)

    txt1.configure(state="normal")
    txt1.delete("1.0", "end")  # Deleting before inserting
    txt1.insert(tk.INSERT, v)
    txt1.configure(state="disabled")


def populate_standard(standard):
    """
    Displays schema field names and descriptions in the data schema information box
    """

    standard_fieldNames = standard["name"]
    standard_descriptions = standard["description"]
    standard_types = standard["type"]
    # ~ standard_pattern = standard.iloc[:,3]

    rows = list()
    for i, elt in enumerate(standard_fieldNames):
        standard_fieldName = elt
        standard_description = standard_descriptions[i]
        standard_type = standard_types[i]
        # ~ standard_patterns = standard_patterns[i]
        row = "%s : %s (%s)" % (standard_fieldName, standard_description, standard_type)
        rows.append(row)

    block = "\n".join(rows)

    txt2.configure(state="normal")
    txt2.delete("1.0", "end")  # Deleting before inserting
    txt2.insert(tk.INSERT, block)
    txt2.configure(state="disabled")


def load_standard(standard_file):

    global standard, standard_name

    standard_name = os.path.basename(standard_file)
    standard = pd.read_csv(standard_file, encoding="iso-8859-1")

    # We display standard label
    lbl2.config(text=standard_name)

    # We display information in the data information box
    populate_standard(standard)

    # Populate comboboxes (list of variables in the right panel)
    populate_source_target(rightframe, data, standard)


def clicked_data():
    """
    When we click on data, we update data information
    and display the columns in the right panel
    """

    global data, data_columns, input_file, input_name, input_name_without_extension, input_name_extension
    global standard, standard_name, standard_file

    # Dialog
    file = filedialog.askopenfilename(
        initialdir=os.path.dirname(__file__), filetypes=[("", ".csv .gpkg .shp")]
    )
    input_file = file
    input_name = os.path.basename(input_file)
    input_name_without_extension = re.search("(.*)\\.(.*)", input_file).group(1)
    input_name_extension = re.search("(.*)\\.(.*)", input_file).group(2)

    data = gpd.read_file(input_file, encoding="utf-8")

    # Drop or not the geometry column
    if input_name_extension == "csv":
        data = data.drop(["geometry"], axis=1)

    # We display information in the data information box
    print_data(data)

    # We display the file name
    lbl1.config(text=input_name)

    # Update data mapping box with the list of columns
    populate_source_target(rightframe, data, standard)

    # Check if standard.csv exists
    p = pathlib.Path(file).parents[0].joinpath("standard.csv")
    if p.is_file():
        MsgBox = tk.messagebox.askquestion(
            "Standard trouvé !",
            "Un fichier standard.csv a été trouvé.\nSouhaitez-vous le charger ?",
            icon="question",
        )
        if MsgBox == "yes":
            load_standard(p)


def clicked_standard():
    """
    When we click on standard, we populate the mapping box
    """

    global standard, standard_name, standard_file

    file = filedialog.askopenfilename(
        initialdir=os.path.dirname(__file__),
        filetypes=[("CSV delimited files", ".csv")],
    )

    load_standard(file)


def clicked_shuffle():
    """
    Refreshes data in the data information box
    """

    if data is not None:
        print_data(data)


def get_columns_mapped():
    """
    Are columns mapped ?
    It traverses the comboboxes to retrieve the matched data schema columns
    The list is of the the length of number or input data columns
    It stores the target field names
    """

    columns_mapped = [elt.get() if elt.current() > 0 else None for elt in combos]
    return columns_mapped


def get_source_target(data):
    """
    We wuild the mapping file
    This file (with suffix -mapping.csb specifies the source and target columns
    """

    from_col = list(data.columns)
    to_col = [
        elt.get() for i, elt in enumerate(combos)
    ]  # combos values define the target column names

    to_col2 = list()
    for i, elt in enumerate(to_col):
        if elt == "NA":
            to_col2.append("_" + from_col[i])
        else:
            to_col2.append(elt)

    d = dict(
        zip(from_col, to_col2)
    )  # this dictionary will be used in the rename function

    return d


def get_renamed_data(data):

    d = get_source_target(data)
    data2 = data.rename(index=str, columns=d)
    return data2


def no_duplicate_columns():
    """
    We control that the target mapping specification is OK
    that is : no duplicate columns
    """

    # Controler
    to_col = [elt.get() for i, elt in enumerate(combos)]
    to_col = [elt for elt in to_col if elt != "NA"]
    n = len(set(to_col))
    if n != len(to_col):
        messagebox.showinfo("Erreur", ("Target columns must be unique"))
        return False
    else:
        return True


def get_type_of_var_in_standard(standard, the_var):
    """
    >>> get_type_of_var(standard, "id_site")
    'integer'
    """

    res = standard[standard["name"] == the_var]["type"].item()
    return res


def is_ok_character(data_var):
    if data_var.dtype == "object":
        return True
    else:
        return False


def is_ok_integer(data_var):

    print("integer")
    if data_var.dtype == "int64":
        return True
    elif data_var.dtype == "float64":
        return (False, "Float type found", None)
    elif data_var.dtype == "object":
        v = [bool(re.match("\d", str(elt))) for elt in list(data_var)]
        i_not_valid = [i for i, elt in enumerate(v) if elt is False]
        if len(i_not_valid) > 0:
            elts_not_valid = [list(data_var)[i] for i in i_not_valid]
            return (False, "String character(s) found", elts_not_valid[1:5])
        else:
            return True
    else:
        return False


def is_ok_float(data_var):
    if data_var.dtype == "float64":
        return True
    elif data_var.dtype == "int64":
        return (True, "Integer type found", None)
    elif data_var.dtype == "object":
        v = [bool(re.match("(\d+\.?\d+)|(\d+\,?\d+)", str(elt))) for elt in data_var]
        i_not_valid = [i for i, elt in enumerate(v) if elt is False]
        if len(i_not_valid) > 0:
            v = [
                bool(re.match("(\d+\.?\d?)|(\d+\,?\d?)", str(elt))) for elt in data_var
            ]
            i_not_valid = [i for i, elt in enumerate(v) if elt is False]
            if len(i_not_valid) > 0:
                elts_not_valid = [list(data_var)[i] for i in i_not_valid]
                return (False, "No float types found", elts_not_valid[1:5])
            else:
                return (True, "Integer type found", None)
        else:
            return True
    else:
        return False


def is_ok_boolean(data_var):
    if data_var.dtype == "bool":
        return True
    elif data_var.dtype == "int64":
        unique_values = list(set(data_var))
        if unique_values == [0, 1] or unique_values in (0, 1):
            return True
        else:
            return (
                False,
                "One or more integer values not equal to 0 or 1",
                unique_values[1:5],
            )
    elif data_var.dtype == "object":

        data_var = data_var.astype("str")

        # Boolean valid values
        ref_bool1 = [["0", "1"], ["O"], ["1"]]
        ref_bool2 = [["FALSE", "TRUE"], ["TRUE"], ["FALSE"]]
        ref_bool3 = [["False", "True"], ["True"], ["False"]]

        # Unique values
        unique_values = sorted(list(set(data_var)))
        if (
            unique_values in ref_bool1
            or unique_values in ref_bool2
            or unique_values in ref_bool3
        ):
            return True
        elif all(
            [
                elt in ["0", "1", "TRUE", "FALSE", "True", "False"]
                for elt in unique_values
            ]
        ):
            return (
                False,
                "Mix of boolean values, for instance TRUE, True, 0 and FALSE at the same time",
                None,
            )
        else:
            return (False, "Wrong values", None)
    else:
        return False


def is_ok_date(data_var):
    if data_var.dtype == "datetime64":
        return True
    elif data_var.dtype == "object":

        if all([control_date(elt) is not None for elt in data_var]):
            return True
        elif all([control_date_alt1(elt) is not None for elt in data_var]):
            return (
                False,
                "Day, month and year in wrong order. Follow ISO-8601 : apply 2021-04-01",
                None,
            )
        elif all([control_date_alt2(elt) is not None for elt in data_var]):
            return (
                False,
                "Years too short. Follow ISO-8601 : apply 2021-04-01",
                None,
            )
        elif all(
            [bool(re.match("[0-9]+-[0-9]+-[0-9]+", elt)) is True for elt in data_var]
        ):
            return (False, "Day(s) not in range", None)
        elif all(
            [bool(re.match("[0-9]+/[0-9]+/[0-9]+", elt)) is True for elt in data_var]
        ):
            return (
                False,
                "Not well formatted. Follow ISO-8601 : apply 2021-04-01",
                None,
            )
        else:
            return (
                False,
                "Dates not valid. Follow ISO-8601 : apply 2021-04-01",
                None,
            )


def is_ok_datetime(data_var):
    if data_var.dtype == "datetime64":
        return True
    elif data_var.dtype == "object":
        elts_not_valid = [
            elt for elt in [control_datetime(elt) for elt in data_var] if elt is None
        ]
        n_not_valid = len(elts_not_valid)
        if n_not_valid > 0:
            return (False, "Wrong datetime", None)
        else:
            return True
    else:
        return False


def is_ok_duration(data_var):
    if data_var.dtype == "datetime64":
        return True
    elif data_var.dtype == "object":
        elts_not_valid = [
            elt for elt in [control_time(elt) for elt in data_var] if elt is None
        ]
        n_not_valid = len(elts_not_valid)
        if n_not_valid > 0:
            return (False, "Wrong time", None)
        else:
            return True
    else:
        return False


def is_ok(data_var, to_type):
    """
    > data_var
    0    a
    1    b
    2    c
    Name: str, dtype: object

    > to_type
    character

    >> True
    """

    if to_type in ("character", "text", "string"):
        return is_ok_character(data_var)

    elif to_type == "integer":
        return is_ok_integer(data_var)

    elif to_type in ("float", "number"):
        return is_ok_float(data_var)

    elif to_type == "boolean":
        return is_ok_boolean(data_var)

    elif to_type == "date":
        return is_ok_date(data_var)

    elif to_type == "datetime":
        return is_ok_datetime(data_var)

    elif to_type == "duration":
        return is_ok_duration(data_var)


def read_data(input_data):

    # !! https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups
    input_extension = pathlib.Path(input_data).suffix

    if input_extension == ".csv":
        file_class = "df"
        data = pd.read_csv(input_data, encoding="utf-8")
    else:
        file_class = "geo"
        data = gpd.read_file(input_data, encoding="utf-8")

    return data


def clicked_check():
    """
    On click on 'Check'
    """

    # Source & Target
    d = get_source_target(data)

    from_cols = list(d.keys())
    to_cols = list(d.values())

    # Remove previous values
    if is_populated is True:
        for elt in labels_control:
            elt.destroy()

    # Change values
    n = len(from_cols)
    for i in range(n):

        from_col = from_cols[i]
        to_col = to_cols[i]

        # Ok or not Ok ?
        if to_col == "_%s" % from_col:
            ok = True
        else:
            data_var = data[from_col]
            target_type = get_type_of_var_in_standard(standard, to_col)

            # Is type correct ?
            ok = is_ok(data_var, target_type)
            print("toto : ", from_col, ok, data_var, "TARGET TYPE : ", target_type)

        # Set text
        if ok == True:
            combo_text = "OK"
            combo_color = "white"
        else:
            combo_text = "NOT OK"
            combo_color = "red"

        label_control = Label(rightframe, text=combo_text, bg=combo_color)
        label_control.grid(row=i, column=2)
        labels_control.append(label_control)


def clicked_rename():
    """
    Renaming is the final operation
    it transforms data in a -mapped file
    and generates a source to target specification file (mapping file)
    """

    ok = no_duplicate_columns()

    if ok is not True:
        return ()

    # Rename data
    data2 = get_renamed_data(data)

    # Are columns mapped
    columns_mapped = get_columns_mapped()

    # Export transformed and restructured data
    output_name = input_name_without_extension + "-mapped"
    output_extension = input_name_extension
    output_file = output_name + "." + output_extension

    if output_extension == "gpkg":
        data2.to_file(output_file, driver="GPKG")
    elif output_extension == "shp":
        data2.to_file(output_file, driver="SHP")
    else:
        data2.to_csv(output_file, index=False, encoding="utf-8")

    # Export data mapping file
    d = get_source_target(data)
    df = pd.DataFrame(data={"from": d.keys(), "to": d.values()})
    output_mapping_name = input_name_without_extension + "-mapping"
    output_mapping = output_mapping_name + ".csv"
    df.to_csv(output_mapping, index=False)

    # Get names
    output_file_name = os.path.basename(output_file)
    output_mapping_name = os.path.basename(output_mapping)

    # Export Log ###################################################

    output_log = input_name_without_extension + "-log.txt"
    output_log_name = os.path.basename(output_log)
    write_log(
        (input_file, output_file, standard_file, output_mapping),
        (standard.iloc[:, 0], standard.iloc[:, 1], columns_mapped),
        output_log,
    )

    # Messages #####################################################

    msg = ("Restructured file -> %s\nMapping file -> %s\n Log -> %s") % (
        output_file_name,
        output_mapping_name,
        output_log_name,
    )
    msg = msg.encode("utf8")
    messagebox.showinfo("Export OK !", msg)


# Window ##################################################

root = tk.Tk()
root.title("Validator-v0.4")


# Data panel ################################################

leftframe = Frame(root)
leftframe.pack(side=tk.LEFT, padx=10, pady=10)

# bouton
btn = Button(leftframe, text="Data", command=clicked_data)
btn.pack(side=tk.TOP)

# Textes
lbl1 = Label(leftframe, text="...")
lbl1.pack(side=tk.TOP)

# Scrolled text
txt1 = scrolledtext.ScrolledText(leftframe, width=40, height=10)
txt1.pack(side=tk.TOP)

# bouton
btn = Button(leftframe, text="Shuffle", command=clicked_shuffle)
btn.pack(side=tk.TOP, pady=10)


# Standard panel #################################################################

rightframe = Frame(root, padx=10, pady=10)
rightframe.pack(side=tk.LEFT)

rightframe1 = Frame(rightframe)
rightframe1.pack(side=tk.TOP)

# Bouton
btn = Button(rightframe1, text="Standard", command=clicked_standard)
btn.pack(side=tk.TOP)

# Textes
lbl2 = Label(rightframe1, text="...")
lbl2.pack(side=tk.TOP)

# Scrolled text
txt2 = scrolledtext.ScrolledText(rightframe1, width=40, height=10)
txt2.pack(side=tk.TOP)


# Matching panel #######################################################################

rightframe2 = Frame(rightframe)
rightframe2.pack(side=tk.TOP)

canvas = Canvas(root, borderwidth=0, background="#ffffff")  # we create the canvas
rightframe = Frame(canvas, background="#ffffff")  # we put the canvas in the frame
vsb = Scrollbar(
    root, orient="vertical", command=canvas.yview
)  # we create the scrollbar and apply it to canvas
canvas.configure(yscrollcommand=vsb.set)  # vsb -> canvas

# Position
vsb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((4, 4), window=rightframe, anchor="nw")

rightframe.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))


# Rename Button Frame #########################################################################

renameframe = Frame(root)
renameframe.pack(side=tk.LEFT, padx=10, pady=10)

checkbutton = Button(renameframe, text="Check", fg="black", command=clicked_check)
checkbutton.pack(side=tk.TOP)

renamebutton = Button(renameframe, text="Rename", fg="black", command=clicked_rename)
renamebutton.pack(side=tk.TOP, pady=10)

root.mainloop()

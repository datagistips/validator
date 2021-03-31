# -*- coding: iso-8859-1 -*-

# DATA
import geopandas as gpd
import pandas as pd

# GUI
from Tkinter import *
import ScrolledText
import ttk
import tkFileDialog
import tkMessageBox

# BASIC
from os import path
import math
import re
import os
import sys
import random
from datetime import datetime

# GLOBAL VARIABLES
global data, standard, input_file, columns_mapped, is_populated
data = None
standard = None
input_file = None
is_populated = False


def write_log(files, columns, log):
	'''
	Write log of transforming file
	- Date and time
	- Input data and Data Schema name
	- Correspondence between Data Schema and Input Data Fields
	'''
	
	f = open(log,"w+")
	
	# Ecriture de la date #########################
	# dd/mm/YY H:M:S
	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	l = ("Date and time : %s\n"%dt_string)	
	f.write(l)
	l = ("------------------------\n")
	f.write(l)

	# Ecriture du fichier source et du standard de destination #########################

	input_name = files[0]
	output_name = files[1]
	standard_name = files[2]
	mapping_name = files[3]
	
	l = ('Input data : %s\n')%(input_name)
	f.write(l)
	l = ('Data schema : %s\n')%(standard_name)
	f.write(l)
	l = ('Data mapping : %s\n')%(mapping_name)
	f.write(l)
	l = ('Output data : %s\n')%(output_name)
	f.write(l)
	
	l = ("------------------------\n")
	f.write(l)
	
	
	# Data Schema
	
	l = ("[SCHEMA]\n")
	f.write(l)
	
	standard_fields = columns[0]
	standard_descriptions = columns[1]
	
	for i, elt in enumerate(standard_fields):
		l = ('%s : %s\n')%(elt, standard_descriptions[i])
		f.write(l)
	l = ("------------------------\n")
	f.write(l)


	# Data Schema conformance #########################
	
	l = ("[SCHEMA <- DATA]\n")
	f.write(l)
	
	columns_mapped = columns[2]
	
	for i, elt in enumerate(standard_fields):
		standard_field = standard_fields[i]
		if standard_field in columns_mapped:
			lib_source_column = str(list(data.columns)[columns_mapped.index(standard_field)])
		else:
			lib_source_column = '__'
		l = ("%s <- %s\n")%(standard_field, lib_source_column)
		f.write(l)
		
	l = ("------------------------\n")
	f.write(l)
	
	
	# Data Transformation #########################
	
	l = ("[DATA -> SCHEMA]\n")
	f.write(l)
	for i, elt in enumerate(list(data.columns)):
		data_colonne = elt
		column_mapped = columns_mapped[i]
		l = ("%s -> %s\n")%(data_colonne, column_mapped if column_mapped is not None else '__')
		f.write(l)
		
	f.close()


def onFrameConfigure(canvas):
	
    canvas.configure(scrollregion=canvas.bbox("all"))


def  print_data(data):
	'''
	Displays data information in the data information box
	'''
    
	rows = list()
	data_colonnes = list(data.columns)
    
	for i in range((data.shape[1]-1)):
		a = data.iloc[:, i].unique()
		if a.dtype == 'int64':
			elts = ['NA' if elt is None else str(elt) for elt in list(a)] # 'NA' if None
		elif a.dtype == 'bool':
			elts = ['TRUE' if elt == True else 'FALSE' for elt in list(a)]
		else:
			elts = ['NA' if elt is None else elt for elt in list(a)]
		
		# We randomly select 10 elements
		# if there are more than 9 unique items
		if(len(elts) > 9):
			elts = random.sample(elts, 10)
		
		v = ','.join(elts)
		v = data_colonnes[i]+' : ' + v
		rows.append(v)
		
	v = '\n'.join(rows)
	
	txt.configure(state='normal')
	txt.delete("1.0", "end") # Deleting before inserting
	txt.insert(INSERT, v)
	txt.configure(state='disabled')
	   

def clicked_data():
	'''
	When we click on data, we update data information
	and display the columns in the right panel
	'''
	
	global data, input_file, input_name, input_name_without_extension, input_name_extension
	
	# Dialog
	file = tkFileDialog.askopenfilename(initialdir= path.dirname(__file__), filetypes=[("", ".csv .gpkg .shp")])
	input_file = file
	input_name = os.path.basename(input_file)
	input_name_without_extension = re.search('(.*)\\.(.*)', file).group(1)
	input_name_extension = re.search('(.*)\\.(.*)', file).group(2)    
    
	data = gpd.read_file(input_file, encoding = "utf-8")
	
	# Drop or not the geometry column
	if input_name_extension == "csv":
		data = data.drop(['geometry'], axis = 1)

	# We display information in the data information box
	print_data(data)

	# We display the file name
	lbl1.config(text=input_name)

	# Update data mapping box with the list of columns
	populate(rightframe, data, standard)
    

def clicked_standard():
	'''
	When we click on standard, we populate the mapping box
	'''

	global standard, standard_name
	
	file = tkFileDialog.askopenfilename(initialdir= path.dirname(__file__), filetypes=[("CSV delimited files", ".csv")])
	input_file = file
	standard  = pd.read_csv(file)
	standard_name = os.path.basename(input_file)

	lbl2.config(text = standard_name)
	
	populate(rightframe, data, standard)
	
	
def clicked_shuffle():
	'''
	Refreshes data in the data information box
	'''
	
	if data is not None:
		print_data(data)
		

def get_columns_mapped():
	'''
	Are columns mapped ?
	It traverses the comboboxes to retrieve the matched data schema columns
	The list is of the the length of number or input data columns
	It stores the target field names
	'''
	
	columns_mapped = [elt.get() if elt.current() >  0 else None for elt in combos]
	return(columns_mapped)
	

def get_mapping_file(data):
	'''
	We build the mapping file
	This file (with suffix -mapping.csb specifies the source and target columns
	'''
	
	from_col = list(data.columns)
	to_col = [elt.get() for elt in combos] # combos values define the target column names
	d = dict(zip(from_col, to_col)) # this dictionary will be used in the rename function
	
	return(d)


def get_renamed_data(data):
	
	d = get_mapping_file(data)
	data2 = data.rename(index=str, columns=d)
	return(data2)
	

def is_ok_destination_columns():
	'''
	We control that the target mapping specification is OK
	that is : no duplicate columns and 
	'''
	
	# Controler
	to_col = [elt.get() for i, elt in enumerate(combos)]
	to_col = [elt for elt in to_col if elt != 'NA']
	n = len(set(to_col))
	if n != len(to_col):
		tkMessageBox.showinfo("Erreur", ("Target columns must be unique"))
		return(False)
	else:
		return(True)
    

def clicked_rename():
	'''
	Renaming is the final operation
	it transforms data in a -mapped file
	and generates a source to target specification file (mapping file)
	'''
	
	ok = is_ok_destination_columns()
	
	if ok is not True:
		return()

	# Rename data #################################################
	
	data2 = get_renamed_data(data)
	
	# Are columns mapped 	
	columns_mapped = get_columns_mapped()

	# Export transformed and restructured data ######################
	output_name = input_name_without_extension + '-mapped'
	output_extension = input_name_extension
	output_file = output_name + '.' + output_extension
	
	if output_extension == 'gpkg':
		data2.to_file(output_file, driver="GPKG")
	elif output_extension == 'shp':
		data2.to_file(output_file, driver="SHP")
	else:
		data2.to_csv(output_file, index = False, encoding='utf-8')
	
	
	# Export data mapping file ##################################
	
	d = get_mapping_file(data)
	df = pd.DataFrame(data = {'from':d.keys(), 'to':d.values()})
	output_mapping = input_name_without_extension + '-mapping.csv'
	df.to_csv(output_mapping, index = False)
	
	# Get names
	output_file_name = os.path.basename(output_file)
	output_mapping_name = os.path.basename(output_mapping)
	
	
	# Export Log ###################################################
	
	output_log = input_name_without_extension + '-log.txt'
	output_log_name = os.path.basename(output_log)
	write_log((input_name, output_file_name, standard_name, output_mapping_name), (standard.iloc[:,0], standard.iloc[:,1], columns_mapped), output_log)
	
	
	# Messages #####################################################

	msg = ("Restructured file -> %s\nMapping file -> %s\n Log -> %s")%(output_file_name, output_mapping_name, output_log_name)
	msg = msg.encode('utf8')
	tkMessageBox.showinfo("Export OK !", msg)


def populate(frame, data = None, standard = None):
	'''
	Function that populates the right panel
	with the source and target columns to match
	'''
	
	if data is not None:
		data_colonnes = list(data.columns)
		
	if standard is not None:
		standard_colonnes = list(standard.iloc[:, 0])
	
	# Block with combo boxes
	# correspond to standard values
	global combos, labels
	
	# Remove elements from the populated panel
	if is_populated is True :
		for elt in combos:
			elt.destroy()
		for elt in labels:
			elt.destroy()
	
	data_colonnes = list(data.columns)
	combos = list()
	labels = list()
	for row, elt in enumerate(data_colonnes):
		if elt != 'geometry': # we don't allow renaming of geometry columns, when data is spatial (gpkg or shp)
			Label(rightframe, text="%s" % elt, bg='white').grid(row=row, column=0)
			
			# If standard file/data is specified
			# then we add the standard columns comboboxes
			# the user will choose in the lists/combos which target column corresponds to each source column
			if standard is not None:
				combo = ttk.Combobox(rightframe)
				combo['values'] = ['_%s'%elt] + standard_colonnes

				# Default position on equivalent source column
				# when source column (data) = standard data column (destination)
				i = [i for i, elt2 in enumerate(combo['values']) if elt == elt2]
				if len(i) > 0:
					combo.current(i[0]) # we position the list on the corresponding item
				else:
					combo.current(0)
				combo.grid(row=row, column=1)

				combos.append(combo) # we add the combo to the list of combos. combos will help when renaming data

# Window ##################################################

root = Tk()
root.title("Validator-v.0.2")


# Left frame ################################################

leftframe = Frame(root)
leftframe.pack( side = LEFT, padx=10, pady=10)

# bouton
btn = Button(leftframe, text="Data", command=clicked_data)
btn.pack(side = TOP)

# Textes
lbl1 = Label(leftframe, text="...")
lbl1.pack(side = TOP)

# Scrolled text
txt = ScrolledText.ScrolledText(leftframe,width=40,height=10)
txt.pack(side = TOP)

# bouton
btn = Button(leftframe, text="Shuffle", command=clicked_shuffle)
btn.pack(side = TOP)
	

# Right Frame #################################################################

rightframe = Frame(root, padx=10, pady=10)
rightframe.pack(side = LEFT)

rightframe1 = Frame(rightframe)
rightframe1.pack(side = TOP)

# Bouton
btn = Button(rightframe1, text="Standard", command=clicked_standard)
btn.pack(side = TOP)

# Textes
lbl2 = Label(rightframe1, text="...")
lbl2.pack(side = TOP)

rightframe2 = Frame(rightframe)
rightframe2.pack(side = TOP)

# Scrollbar
canvas = Canvas(root, borderwidth=0, background="#ffffff") # we create the canvas
rightframe = Frame(canvas, background="#ffffff") # we put the canvas in the frame
vsb = Scrollbar(root, orient="vertical", command=canvas.yview) # we create the scrollbar and apply it to canvas
canvas.configure(yscrollcommand=vsb.set) # vsb -> canvas

# Position
vsb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((4,4), window=rightframe, anchor="nw")

rightframe.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))


# Rename Button Frame #########################################################################

renameframe = Frame(root)
renameframe.pack( side = LEFT, padx=10, pady=10)

renamebutton = Button(renameframe, text="Rename", fg="black", command=clicked_rename)
renamebutton.pack( side = LEFT)

root.mainloop()

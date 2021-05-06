# validator

Validator is a data exploration 🔍, validation ✔️ and restructuration ↔️ assistant.

![](images/demo.gif)

## Install
[Install Python (for instance, v3.9)](https://www.python.org/downloads/)

Once python installed, open your Command Line Interface and type :

	git clone https://github.com/datagistips/validator.git # clones validator from github
	pip install -r requirements.txt                        # installs libraries
	cd validator                                           # enters validator folder
	python validator-gui.py                                # launches validator

## 📘 Quick start (in 4️⃣ steps)
**Launch** validator

	python validator-gui.py

1️⃣ Load your **data**

![](images/load-data.png)

 **Shuffle**🔄 your data, to explore unique values.

![](images/demo-shuffle.gif)

2️⃣ Load your **schema** (where first column of the CSV defines the field name)

![](images/standard.png)

3️⃣ **Match** the source field names of your data to your target field names

![](images/match.png)

> If source and target names are the same, they will be automatically matched (like `id_site` in the above example).

4️⃣ **Export** the result

![](images/rename.png)

## 📄 Output files

There are 3 output files.

![](images/exports.png)

1. the **restructured** data with suffix `-mapped`
2. the **mapping or matching file** with suffix `-mapping` which contains source and target field names

	![](images/mapping.png)

3. a **log** `-log` with date time, input data and data schema name, details on schema conformance and data transformation.

	![](images/log.png)

## 📄 Data formats
Input data format can be either CSV, Geopackage (GPKG) or ESRI Shapefiles (SHP).

## 🔎 Details
### 🔄 Shuffle
In the exploration box, only 10 unique values are displayed, but you can shuffle your data to explore more unique values.

### 💻 The data mapping file
The data mapping file **keeps track** of your restructuration process. You can use this file in other CLI programs or scripts to restructure other pools of data programmatically.

## 🚗 Road map
- control data types (integer, float, etc...)
- control regexes (`^[A-Za-z\s\-\u00C0-\u00FF]+$`, etc...)
- CLI Program

## Author & Licence
- Mathieu Rajerison
- Current version : v.0.3 [(check CHANGELOG for version details)](CHANGELOG.md)
- Creation date : 30th of March 2021
- Licence : Affero-GPL



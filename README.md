# Detection-of-Convective-Initiation
Codes for the detection of convective inititation from CIWS and HRRR output.

This repository includes the pyhton codes to detect Convective Initiation objects using the output from the weather models (products) HRRR and CIWS. 
The codes also include population of a database using PostgreSQL.

Below is the detailed summary of the database and the code structure.


Database
---------

Tables in the database contain data from different products, threshold sensitivities etc. My initial motivation was to create a single table to contain any data (e.g., CIWS, HRRR, region, level etc.) but as I worked on the project, it became clear to me that keeping everything in single table slows down the reading/writing, so I ended up creating separate tables. For example:

Object_repo_se_18 (southeast region for CIWS containing CI candidates using 18 km previous time-step proximity threshold)

However, all tables share the similar structure and the only changes in the columns are the CI candidate and tracking columns depending on the thresholds. The general idea is that, each row contains the information for a single object for a given product, variable, valid, issue, lead, region and level (altitude or model level). Object_repo_se_18 columns:

Src: The product name (‘CIWS’, ‘HRRR’)
Datetime: Valid time (maybe should be renamed as valid)
Issue: Issuance hour in integer (999 for CIWS)
Lead: Lead minutes in integer (999 for CIWS)
Level: Model level altitude in integer (as of now only 0 because VIL is a surface variable)
Th: Threshold used to identify objects
Bounds: The i,j bounds of the region showing {{x1,y1},{x2,y2}}
Id: the sequential identification number for each object (unique field). This column is used in object tracking
Obj_num: The number of the object in a given field (not a very important field, kinda redundant, can be deleted making sure the code is changed accordingly)
Obj_ij: The i,j values of all the grid boxes that make up the object (array)
Obj_cmass: The I,j values of the center of mass of the object (array)
Obj_area: The area of the object
Obj_mean: The mean value of the variable (VIL) values within the boundaries of the object
Obj_max: The max value of the variable (VIL) values within the boundaries of the object
Info: A general information column that can be populated by anything that would help

The fields above are general object characteristics. Columns specifically related to CI identification and tracking are below:

Ci: This is the binary column for ci candidates. It indicates the object in the specific row is a CI candidate if 1, and not if NULL. This column is for 5-min resolution. There are also similar columns, for example ci_15_18, for 15 minute, 18 km proximity threshold.
Ci_evol: This is also a binary field (1 or NULL) for plotting purposes. Indicates the evolution objects as a result of tracking. If 1, they are plotted as yellow. It doesn’t indicate the CI candidate being tracked, the next column does that. So, this column is in a way redundant, the plotting can also be done using the next column.
Ci_track: This is an array field to identify tracked objects using the id column. The default value of the column is an empty array so that multiple object ids can be inserted. For example, if a row has {4,25,167} in this column, it means that the object stored in this column is the continuation of three CI candidates with the ids 4, 25, and 167. This way, a single CI candidate can be queried to form get its evolution (i.e. get all objects where 4 exists in the CI_track array). This requires an index on this column using GIN in order to speed up the query. 

There can be variations of both ci_evol and ci_track columns depending on the thresholds. For example, ci_evol_15_18q15: for 15 minute, 18 km previous time-step proximity, Q=15.  


CI Codes 
--------

computeCI_{product}.py: This is the main code that imports the detection and tracking algorithms. The comments in the code explains the working structure. My preference is first running the lines (1), (2), and (3) separately while others are commented out. 

ObjDetectAtt_v2_db.py: This is the region growing algorithm that reads each file, objectize the field and write the objects together with their attributes (the attributes before * above) to the database.

CI_detect_PrevTime.py: The CI candidate detection algorithm that uses only the previous time-step proximity threshold. This algorithm updates the ci, ci_15 etc. in the database.

CI_track_MtoM_{product}.py: The many-to-many tracking algorithm. Updates the ci_evol and ci_track columns in the database. The parallelization for this code is really not doing much, so as of now it is slow. It should be optimized.

config_CI_{product}.py: Configuration file that contains various constant values (thresholds, table names, variable names etc.)

db_utils_CI.py: Contains many database queries as functions. I created this separately not to have all the database related codes in the main codes above. There are several queries I used in the beginning but then replaced with others, but I didn’t delete the old ones from this file.

Analysis Codes 
--------------

CI_dist_ts.py: This is the code to read the database and plot Area/MaxVIL distributions, and object count time series for both CIWS and HRRR. The comments in the code should be explanatory enough how to change parameters to get different plots.

CI_track_results.py: This is the code to output tracking results (e.g., how much of the CI candidates become VIP 3 with varying Q). This code outputs the numbers, then I feed the numbers manually to the code below to create bar charts.

CI_track_results_plot.py: Plot bar charts with numbers obtained from the above code.


Object Plotting Codes 
---------------------

VarObj_Plot_{product}.py: These codes plot the object and the VIL field side by side with indication of CI_candidates (red) and continuations (yellow). There are some other plotting routines I did under the same folder, but not used in the report.



PS: For all the analysis and the plotting codes, the time periods and the lat/lon of the regions have to be entered otherwise the database queries will return none. This can be generalized by incorporating the time and the region in the config files.


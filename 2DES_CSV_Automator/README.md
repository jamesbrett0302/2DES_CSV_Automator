# **README – How to use and edit the Tecan Excel-to-CSV Power Automate flow**

### **What this flow does**

This script allow automatic data extraction + formatting from Tecan Data Files into [2DES\_Studio](https://github.com/jamesbrett0302/2DES_studio) compliant .csv files



It works by:

1. Opens Tecan data file
2. Reads fluorescence scan data for multiple samples
3. Rearranges the data for each sample into a 2DES\_Studio compliant .csv file
4. Saves one .csv file per sample, named after the well plate position of that sample e.g. A1, B2, C3 etc



### **How to acquire this flow**

Windows Power Automate (Desktop) is an application likely already on your PC (Install [here](https://learn.microsoft.com/en-us/power-automate/desktop-flows/install) if not), load the application, sign in and select the "Flows" section on the left-hand panel



In the "Flows" section click "+ New" in the top left > Flow > Name your flow > Sequence mode > Enable Power Fx > Create



Copy the contents of 2D Tecan Automator.txt and paste (CTRL+V) into the empty flow page on Windows Power Automate



A script containing 67 lines should appear (Errors may be present - Errors marked by an orange triangle are safe to ignore. Errors marked by a red circle must be fixed before the flow can be executed



### **Before running this flow**

#### Lines to change

Line 5-12 contain variables which will change depending on your specific experiment



* Line 5 - **FirstSampleRow** - This is the row of the first sample data in the first scan block - Change this if the first sample is no longer on row 36
* Line 6 - **LastSampleRow** - This is the row of the last sample data in the first scan block - Change this if the last sample is no longer on row 75
* Line 7 - **RowsPerScan** - This is the number of rows from one scan block to the next scan block - RowsPerScan can be calculated by taking the row number of your first sample cell and subtracting it from the row number of the next one - For example, if the first scan begins on 36 and the second scan begins on 105 then, 105 - 36 = 69 = RowsPerScan
* Line 8 - **EmissionPointCount** - This is the number of emission wavelength data points in the first scan - This can be found by highlighting the Emission Wavelength row in excel (typically row 35), looking at the "Count" on the bottom panel of excel and subtracting 1
* Line 9 - **PointsDiscardedPerScan** - This is how many fewer data points are read on each new scan - In a typical 2D Tecan experiment as the Excitation Wavelength increases so does the lowest Emission Wavelength, so a smaller range is scanned.
* Line 10 - **FirstExcitationRow** - This is the row containing the excitation wavelength for the first scan block - Change this if the first Excitation Wavelength is not stored in row 21
* Line 11 - **LastExcitationRow** - This is the row containing the excitation wavelength for the final scan block - Change this if the final Excitation Wavelength is not stored in row 2643
* Line 12 - **OutputFolder** - This is where the CSV files will be saved - In the file explorer, navigate to where you want to save your .csv files. Click the breadcrumb box at the top, copy and then paste that file path into line 12



#### Lines not usually changed

Line 15 - **SampleRow Loop** - This is not a variable but a loop but ensures every sample is processed. If you do not wish to process all of your samples it is safer to edit "Line 5" and "Line 6" such that the new range spans the samples you would like to process, i.e. Line 5 = 38 and Line 6 = 39, only 2 samples will be processed: 38 and 39.



### **Running the flow**

Once your variables have been set for your specific data file, click "Publish" at the top. This will allow you to run this flow without the edit screen showing, which significantly increases to speed at which the flow runs.



Back on the main window of Power Automate, in the "Flows" section your new flow should be visible. Hover your mouse over it and click the "Run" icon



A dialog box will open > Select your data file > Open



Your data file will open in excel along with a .csv file, likely named A1, and data will begin appearing in your .csv file



Avoid doing any actions in any excel windows that opens a dialog box (saving, closing, searching etc) as this will cause the script to fail. The windows can be minimised and left to run in the background.



The flow can be stopped at any point by hovering over the flow in the main Power Automate window and click the "Stop" icon.



It is a good idea to just run one or two samples first to ensure your variables have been set up properly.



### **Common problems**

###### Problem: Too many or too few samples processed

Check:

line 5 (**FirstSampleRow)**

line 6 (**LastSampleRow)**



###### Problem: Data from later scans is misaligned

Check:

line 7 (**RowsPerScan**)



###### Problem: Not enough or too many emission values read

Check:

line 8 (**EmissionPointCount**)



###### Problem: Scan count is wrong

Check:

line 10 (**FirstExcitationRow**)

line 11 (**LastExcitationRow**)

line 7 (**RowsPerScan**)



###### Problem: CSV files saved in the wrong place

Check:

line 12 (**OutputFolder**)



###### Problem: Too many or few data points are discarded between scans

Check:

Line 9 (**PointsDiscardedPerScan)**



#### **Recommended naming for saved versions**

It is a good idea to save copies of the flow for different experiment formats, for example:



* Tecan\_39rowspacing
* Tecan\_69rowspacing
* Tecan\_115points
* Tecan\_104points



That way you can always go back if needed.


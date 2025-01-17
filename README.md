# SBOL-Sample-Creator

[![Build Status](https://travis-ci.org/TASBE/SBOL-Sample-Creator.svg?branch=master)](https://travis-ci.org/TASBE/SBOL-Sample-Creator) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/TASBE/SBOL-Sample-Creator/master?filepath=SynBioHub%20Data%20Visualization.ipynb)

Create SBOL sample descriptions from Excel and upload them to SynBioHub.

## Getting Started
To access the notebook immediately through a browser, click on the blue **"launch | binder"** button next to the title above. This may take a few minutes but does not require you to install any modules.
*Note: if you leave the notebook inactive for 10 minutes, the browser will shut down and the notebook will need to be reloaded.*


Otherwise, follow the instructions below if you want to run this notebook locally (from your terminal):
This project requires that you have Jupyter and Python 3 installed on your computer, as well as some additional modules and libraries.
Installation instructions for Jupyter can be found here: https://jupyter.org/install
It is recommended to use Anaconda to do this because it automatically installs both Jupyter Notebook and Python -- installation instructions can also be found through the link above.

## Installation
In terminal, access the root directory of this project (SBOL-Sample-Creator-master). Run the installation script with the following command:
```
./install
```
This will install all necessary libraries and jupyter extensions onto your computer.

## How to use the notebook
If running on terminal, make sure you are in the root directory and run the following command:
```
jupyter notebook SynBioHub\ Data\ Visualization.ipynb
```
This should open up the notebook in a new tab on your browser. 

To use the notebook, click the "Browse Files" button and select your Excel file. Currently only one file can be run at a time.

Then, select the "Proceed" button to start the conversion process. You should see a progress bar with the name of your file in it. If there is an error or file formatting that the program cannot understand, it will stop and tell you what to do. 
You will have to reupload the file for any changes you make to take effect. Here is an error example:

![](img/errorexample.gif)

If there were no errors, continue to the next section where you will enter information about your project and experiments. The format that this notebook follows assumes you have a general Project collection, containing multiple Experiment collections that can be derived from different Excel spreadsheets. 

If you already have an existing Project collection in your SynBioHub account, in the first section you only need to enter the displayID and version of that Project. If you want to create a new Project, a name and description can be added as well. Make sure the displayID has only letters, numbers, or underscore characters and that it does not begin with a number. The displayID will be part of the URI, or uniform resource identifier for your collection.
The name can be whatever you want it to be -- it gives greater specificity to your collection.

In the second section, enter the displayID, name, and description of the new Experiment collection you want to create. The collection version will be automatically set as 1.0.0 or 1 depending on what version of pySBOL you are using.

![](img/HowToUse.gif)

Finally, enter your SynBioHub username and password and click the "Upload to SynBioHub" button. If creating a new Project you will have the option to confirm its displayID before proceeding. If all is well, you should see a "Successfully Uploaded" message and a link that will take you to your updated Project on SynBioHub!

**Note: depending on the size of the Excel file, uploading may take 1-2 minutes so do not be alarmed if it seems like it is taking a while.**

To delete specific Samples, you can click on the trash icon next to the Sample name. 


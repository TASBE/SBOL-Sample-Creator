# SBOL-Sample-Creator [![Build Status](https://travis-ci.org/TASBE/SBOL-Sample-Creator.svg?branch=master)](https://travis-ci.org/TASBE/SBOL-Sample-Creator) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/TASBE/SBOL-Sample-Creator/master?filepath=SynBioHub%20Data%20Visualization.ipynb)
Create SBOL sample descriptions from Excel and upload them to SynBioHub.

## Getting Started
To access the notebook immediately through a browser, click on the blue **"launch | binder"** button next to the title above. This may take a few minutes but does not require you to install any modules.


Otherwise, follow the instructions below if you want to run this notebook locally (from your terminal):
This project requires that you have Jupyter and Python 3 installed on your computer, as well as some additional modules and libraries that are detailed below.
Installation instructions for Jupyter can be found here: https://jupyter.org/install
It is recommended to use Anaconda to do this because it automatically installs both Jupyter Notebook and Python -- installation instructions can also be found through the link above.

## Installation
#### 1. First, you will need to install Jupyter extensions:
```
pip3 install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user
```
or, if using Anaconda:
```
conda install -c conda-forge jupyter_contrib_nbextensions
```

#### 2. Install ipywidgets:
```
pip3 install ipywidgets
jupyter nbextension enable --py widgetsnbextension
```
or, if using Anaconda:
```
conda install -c conda-forge ipywidgets
```

#### 3. Install ipyupload:
```
pip3 install ipyupload
jupyter nbextension install ipyupload --py --sys-prefix
```

#### 4. Now you need to make sure you have pySBOL installed for Python 3. Run the following commands from your terminal or console.
More detailed instructions (and troubleshooting) can be found here: https://pysbol2.readthedocs.io/en/latest/installation.html\
```
pip3 install pysbol
```
or, if that causes a permission error:
```
git clone https://github.com/SynBioDex/pysbol.git
```
and then, from within the package's root directory:
```
python3 setup.py install
```

#### 5. Install xlrd, the library that will handle all the Excel data manipulation:
```
pip3 install xlrd
```

#### 6. Finally, install tqdm, the library that allows the progress bar of your upload to show:
```
pip3 install tqdm
```
or, if using anaconda:
```
conda install -c conda-forge tqdm
```

## How to use the notebook
Download "SynBioHub Data Visualization.ipynb" and "experimentdnaexcel.py" into the directory that contains the Excel file you want to convert to SBOL.
"cd" to that location inside of your terminal or console, and then run the following command:
```
jupyter notebook SynBioHub\ Data\ Visualization.ipynb
```
This should open up the notebook in a new tab on your browser. 

Click the "Upload" button and select your Excel file. Currently only one file can be run at a time.

Then, select the "Proceed" button to start the conversion process. You should see a progress bar with the name of your file in it. If there is an error or file formatting that the program cannot understand, it will stop and tell you what to do. 
You will have to reupload the file for any changes you make to take effect. Here is an error example:

![](img/errorexample.gif)

If there were no errors, continue to the next section where you will enter information about your project and experiments. The format that this notebook follows assumes you have a general Project collection, containing multiple Experiment collections that can be derived from different Excel spreadsheets. 
If you already have an existing Project collection in your SynBioHub account, in the first section you only need to enter the displayID and version of that Project. If you want to create a new Project, a name and description can be added in addition. Make sure the displayID has only letters, numbers, or underscore characters and that it does not begin with a number. The displayID will be part of the URI, or uniform resource identifier for your collection.
The name can be whatever you want it to be-- it gives greater specificity to your collection.

In the second section, enter the displayID, name, and description of the new Experiment collection you want to create. The collection version will be automatically set as 1.0.0 or 1 depending on what version of pySBOL you are using.

![](img/HowToUse.gif)

Finally, enter your SynBioHub username and password and click the "Upload to SynBioHub" button. If creating a new Project you will have the option to confirm its displayID before proceeding. If all is well, you should see a "Successfully Uploaded" message and a link that will take you to your updated Project on SynBioHub!


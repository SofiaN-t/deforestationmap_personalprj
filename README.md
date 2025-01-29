# Introduction
This tool is the outcome of a Master Thesis and was delivered to an NGO foundation. It is designed to visually represent a map with three distinct layers and was developed to help relevant stakeholders to assess the risk of coffee farms being situated within or in the proximity of deforested areas. The map is hosted at a dedicated website, streamlit. Since the provided geospatial data of the coffee farms are under an NDA, a fictional geometry is used here to materialise the map.

It consists of two main pages. The first one includes an interactive map visualising the different layers with filtering functionalities. The second page informs the user on intersections on a coffee farm basis via a tabular view. There is also a third auxiliary page that shares basic information on the alert datasets and points to the relevant websites while also explaining the basic functionality of the dashboard.

# Instalation
It is advisable to make a dedicated virtual environment for this project, as there are special libraries used

1. Create and activate a virtual environment in your project directory.

```bash
python -m venv venv
<virtual-env-name>\Scripts\activate.bat # On Windows
```

If you select to name your virtual environment under a different name, please make sure that you rename this in the .gitignore file accorsingly, before you make the repository.


2. Install project dependencies

```bash
pip install -r requirements.txt
```

You should now have a dedicated virtual environment for the project.

# Structure
When opening your project directory, this is the structure that you should encounter: 

```bash
├── venv
├── app/
│   ├── 0_Map.py
│   └── pages/
│       │   └── 1_Intersection_table.py
│       │   └── 2_Background.py  
├── data/
│   └── input/
│       ├── raw/
│       │   ├── perdida_de_bosque/ 
│       │   └── 10N_080.tif
│       │   └── export_demo.xlsx      
│       └── processed/
│       │   └── amaz_gdf.geojson
│       │   └── intersection.csv
│       │   └── processed_export_demo.geojson   
│       │   └── radd_gdf.geojson   
├── scripts/
│   ├── find_intersectio.py
│   ├── read_open_source_data.py
│   ├── transform_provided_raw_file.py
│   └── exploratory/
│       └── plot_all_datasets.py   
│       └── raster_vector_overlap.py 
├── .gitignore
├── config.json
├── README.md
├── requirements.txt
└── utils.py
```

# Paths configuration
There are two auxiliary files that take care of the paths configuration. Currently, configuration file `config.json` specifies the root and the data folder paths. File `utils.py` locates and loads the configuration file and loads the specified paths. 

# Data processing
After having setup the environment, the files used for the dashboard need to be produced. Folder `scripts` includes the code for the processing. 

To ensure reproducibility, an adjustment to some file paths needs to be made. If the zip file is unpacked as is, the data paths in `config.json` should remain the same. Although not strictly used, we suggest that the root_path is changed to the root directory of the project. When a different folder structure is desired, the configuration will need to be changed to reflect the new structure.

With these changes, we proceed to explain the developed scripts and the order in which they need to run.

## Mandatory
**1.** `transform_provided_raw_file.py` is the script that needs to run first. It produces a geojson file with the available relevant information for the provided coffee plots. In this case, an excel file is the input for the script (`data/input/raw/export_demo.xlsx`). We assume that any provided file with information on the coffee farms will be of similar if not the same format. After some basic manipulation, a geojson file is produced and saved (`data/input/processed/processed_export_demo.geojson`). This file contains vector data which is a geographic data type where data is stored as a collection of points, lines, or polygons as pairs of (x,y) coordinates along with other non-spatial related attributes. Geojson is a typical format for geospatial data and is easy to be read and transformed with a standard for geospatial applications library, geopandas (which draws from pandas).
This file will be used later both for further development and for the dashboard. 

The output of this script should be a file titled `porcessed_export_demo.geojson` in the folder `path data\input\processed`.

**2.** `read_open_source_data.py` should run, next. It produces two geojson files having as sources two open-source datasets.

First, a dataset for the Amazonian Colombia alerts (`data/input/raw/perdida_de_bosque/TMAPB_Region_100K_2020_2022.shp`) is loaded. Please be informed that the other files in the same folder might be necessary for the reading of this dataset. The dataset is, then, transformed to a desirable format. The details of the transformations can be found in the script. Then, it is saved in a geojson file, similar to the script above where we process the raw file with the coffee farms. This file will be later used for the development of the dashboard.

Next, a dataset for the RADD alerts is loaded (`data/input/raw/10N_080W.tif`). This needs more extensive transformation, as the type is of raster data. A raster data type is made up of pixels or cells and each pixel has an associated value. A grid of (usually square) pixels make up a raster image with the purpose of displaying a detailed image (a map, in our case). With the use of an affine transformation, the image coordinates (rows and columns) are mapped to the world geographic (x,y) coordinates. Since the raw file is a high-resolution image, only a window of the data is read, based on the bounds of the coffee farms plots. Within this window, we isolate the polygons for which there has been an alert and collect it to a geojson FeatureCollection. This is finally saved in a geojson format, similar to the other cases. The produced file is then enriched with some necessary information, such as the year of the alert and the confidence level of the alert, before it is saved again. This file will also be later used for the development of the dashboard. Please note that typically this type of file (.geotiff) needs to be processed in chunks due to their size.

The outcome of this script should be able to find two files titled in the folder path `data\input\processed`, titled `amaz_gdf.geojson` & `radd_gdf.geojson`.

**3.** `find_intersection.py` needs to run last. This script loads the three processed geojson files and combines the datasets with the alerts into one, specifying the source of each row. This part of the code is commented out but can be reactivated, when a meaningful third target dataset is available. Then, making use of a readily available geopandas function (sjoin), it looks for intersections between the coffee plots and the two alerts datasets. The function merges data from one set of geographical features with another set based on their locations and spatial interaction. It is not computationally expensive because of the way it operates. When it is required, Geopandas creates indices that represent the bounding boxes of the geometries (bounding boxes are the minima and maxima of the x and y coordinates of each geometry). When those do not satisfy the spatial relationship in question, the particular geometries will not. This step significantly reduces the number of detailed geometric calculations needed. The spatial relationship checked here is the intersection which is the most general of all and is true when the boundaries and/or interiors of the two geometries intersect in any way. 

When an intersection is found to be satisfied, geopandas merges the correspoding rows from each dataset. Thus, the sjoin function returns a new geodataframe that includes combined data from both input frames for the pairs of geometries that meet the criteria. To be more specific, the original result returns the columns from the left geodataframe, namely `plot_name`, `plot_id` and `geometry` and the columns from the right geodataframe (excluding the geometry), while adding an `index_right` column to indicate the index of the right geodataframe (which is the alerts geodataframe) with which the corresponding coffee plot intersect. The result is then adjusted to remove unnecessary columns and create more informative ones. When no intersection is found, a dataframe with columns identifying the coffee plots (name, id) and the alerts ('Amazonian', 'RADD') specifying 'No intersection' is returned. In both cases, the result is saved in a csv file that will be later used for the dashboard development.

The outcome of this script should be able to find a file titled `intersection.csv` in the folder path `data\input\processed`.

## Exploratory
Folder `exploratory` includes two python scripts that were developed at an earlier stage of the project. They are included as a guide in case raster *and* vector data need to be plotted together and for the case that an overlap between those datasets needs to be identified.

**1.** `plot_all_datasets.py`: Here, a plot is produced when the inputs are the two vector datasets (coffee farms & amazonian alerts) and a raster dataset (in this case RADD alerts before transforming it to a geojson format).

A plot is expected as an outcome of this script and is not used further anywhere.

**2.** `raster_vector_overlap.py`: Here, the script processes a raster file and a vector file to identify the intersection between the two datasets, storing the results in a dictionary. It makes a mask for the vector data to align the shapes with the raster grid. The raster data is processed in chunks, filters only for the alert values based on the threshold, compares each chunk with the corresponding section of the vector mask. Whenever overlaps were detected, the global positions of these intersecting pixels were recorded. However, the vector geometry that overlaps is not recorded here, which would be desirable.

The output of this script is a dictionary and is not used further anywhere.

# Streamlit dashboard
The code for the dashboard development can be found in folder 'app'. Streamlit, where this app is hosted, can support multi-page applications. The main page needs to be at the same level with a folder named 'pages' where the code for the other pages is developed. This is the approach followed here.

1. The main page, where the application lands is titled '0_Map.py' and can be found in folder 'app'. Here, we load all the processed geojson files and produce a map with folium library. Folium builds on the data wrangling strengths of the Python ecosystem and the mapping strengths of the Leaflet.js library and therefore is selected for this tool. 

Before making the datasets available, some basic page configuration is setup. Then, we load the data and build the map. The plotting function is built adding the components (tooltip, style, map layer) layer by layer. Detailed descriptions can be found in the code. Then, an html title and legend are built. Please be advised that the legend  is relative to the styling choices and its positioning is based on the current situation. 

Before the map is rendered, some filtering options at the sidebar are defined. Here, we define checkboxes for the available years and confidence levels of the RADD alerts, filtering the corresponding dataset accordingly.

Finally, the map is rendered and displayed. This page is the one which loads the datasets and builds the map so, it might take some time to produce.

2. The second page of the dashboard can be found in the pages folder and is titled '1_Intersection_table.py'. Here, we simply load a pre-made file with the intersections found and show it as a table. We chose to make the file before the dashboard development so that the processing time is short. In case this is not desirable, the intersections can be calculated while the dashboard is being produced by incorporating the code from script 'find_intersection.py'.

3. The last page includes a short description of the dashboard including the raw data sources

To run the dashboard locally,
1. Open a terminal
2. Navigate to the folder where you store this code
3. Activate the virtual environment (if applicable) 
4. Launch the streamlit app

```bash
streamlit run app\0_Map.py
```

The map page should be automatically opened in your web browser. If not, a local URL should be printed on your prompt, which you can follow. There is a left sidebar which you can use to navigate between pages. Below this, you find the filtering area as mentioned above. Selecting and de-selecting will automatically change the map that you can find on the right (this, will take some time). The user can zoom-in and zoom-out of the map by using the button on the top left corner. On the right top corner, there is a toggle button which can be used to select which datasets will be visible on the map. On the bottom left corner, the legend can be found.

Navigating to the second page, a table in standard format can be found, showing the intersections. The table can be downloaded by pressing the download button appearing at the top right corner of the table when hovering over it.

When there is a saved change at the backend of the dashbaord and the app is still open, you can automatically select to rerun the app, finding the corresponding button at the top right side of the web browser page. 


# Streamlit application deployed
The web application can now be deployed to the Streamlit Cloud. To do so: 

1. Visit https://streamlit.io and Sign Up with your GitHub account giving the required permissions. 
2. Then click on the *New app* button. 
3. Select the GitHub repository of the project.
4. Choose the main branch. 
5. Set the *Main file path* to `Map.py`
6. Modify the app URL to something representative You can only modify the first part of the URL.
7. Optionally, go to Advanced Settings to modify the Python Version of the app. 
8. Finally you can click on the *Deploy* button and wait for the deployment to finish. This may take a few minutes. After that you will be able to see the dashboard online at the URL you specified above.

Now, after every new code change that is pushed to the remote repository, the web application will be automatically updated in the Streamlit Cloud including the new changes.

Please note that deploying from a private repository is only allowed one at a time.
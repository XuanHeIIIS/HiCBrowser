# HiCBrowser : A simple web browser to visualize Hi-C and other genomic tracks

Fidel Ramirez, José Villaveces, Vivek Bhardwaj  

## Installation

You can install HiCBrowser using pip :

```r
pip install git+git//github.com/maxplanck-ie/HiCBrowse@master
```

You can also download/clone this GitHub repository and run the setup.py script inside :


```r
cd HiCBrowser
python setup.py install -f
```


## Usage

### Install HiCExplorer

HiCBrowser works using [**HiCExplorer**](http://hicexplorer.readthedocs.io/en/latest/) in the background. Thus, you need to [install HiCExplorer](http://hicexplorer.readthedocs.io/en/latest/content/installation.html) first.

If HiCExplorer and or HiCBrowser is not properly installed (by running setup.py) it may be required to set the $PYTHONPATH. Specially for development it is quite convenient not to install the packages:


```python
# ON COMMAND LINE
export PYTHONPATH=/path/to/HiCExplorer:/path/to/HiCBrowser
```

### Test run

The folder `example_browser` contains all data and config files to run the browser. This is _Drosophila melanogaster_ data only for chromosome X. To start the example server simply type:

```r
cd example_browser
bash run_server.sh
```

### Prepare files

HiCBrowser needs three config files.

+ **region tracks** : To visualize all genomic tracks for given regions. (eg. [gene_tracks.ini](./gene_tracks.ini))
+ **gene tracks** : To visualize TADs near given gene. (eg. [region_tracks.ini](./region_tracks.ini))
+ **browser config file** : To providing information about directories to save images and the two tracks above. (eg. [browserConfig.ini](./browserConfig.ini))

We have provided example for each of these files with the package, as shown above. For a full documentation of what types of data can be plotted in the region tracks 
and for extended examples please look at the [documentation of the plotTADs](http://hicexplorer.readthedocs.io/en/latest/content/tools/hicPlotTADs.html) 
function of [HiCExplorer](http://hicexplorer.readthedocs.io/en/latest/)  


### Run

To run the browser, simply run **runBrowser** command, as shown below.

        

```r
# --config = browser config file
# --port = localhost port to run the server

runBrowser --config browserConfig.ini --port 8888 --numProcessors 10 
```

## Help

Contact our googleGroup **hicexplorer@googlegroup.com** for further help with HiCBrowser or HiCExplorer.

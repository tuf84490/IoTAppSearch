## IoT App Search
This script will download, decompile, and search through android IoT apps for vulnerabilites. Given an app ID, it will search through the app for specified strings in the config.txt file. Once found it will output the resulting matches in an output text file named after the app ID. 

### How to use
First get the app ID of the app you want to check. The app ID can be found in the URL on the google play store page, following the id= parameter. For example : ![](AppId.JPG)

Then take the app Id and run the command below (ensure python is installed) : 
```
python main.py com.example.app.id
```

If you wish to use only certain aspects of the script, you can specify parameters at the end to skip cetrain steps. Specify a 1 as the last parameter to only download the app, or specify a 2 as the last parameter to only unpackage and scan an already downloaded apk.

#### Download only example
```
python main.py com.example.app.id 1
```
#### Decompile and scan only example
```
python main.py com.example.app.id 2
```
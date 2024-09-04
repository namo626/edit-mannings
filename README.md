## Install
Clone this repo, and inside it run
```
pip install .
```
This creates an executable `edit-mannings` in the environment.

## Usage
Run
```
edit-mannings --help
```
for options. The user specifies the fort.13 and fort.14 files. Optionally, choose a criteria for selecting the nodes to be modified, and a modifier to modify the corresponding Manning's n attributes. For example,
```
edit-mannings fort.13 fort.14 --criteria 1 --modifier 2 --factor 5 -o fort.13.mult5
```
will create a file `fort.13.mult5` which has the Manning's n of the nodes inside the Galveston bay area (`criteria`) multiplied by 5 (`modifier` and `factor`).

# Disomy test
Ronald Moura
2025-01-13

## Introduction

This tool takes PLINK files (.ped and .map), calculate Mendelian Errors, 
using Plink 1.90, then plots the distribution of erros among chromosomes, 
highlighting the chromosome with most errors.

## Requirements

- Miniconda 

## Installation

1. clone this repository to your computer
2. download and install Miniconda using this link: https://www.anaconda.com/download/success
3. use the .yaml file to create an envrionment:

``` sh
conda env create -f environment.yml
```
4. place the folder with your files inside this folder and hit the following commnad:

``` sh
python disomy_test.py fid iid father_id mother_id --directory sample_folder
```
Where:

>positional arguments:
>  fid                   family ID.
>  iid                   individual ID.
>  father_id             paternal ID.
>  mother_id             maternal ID.
>
>options:
>  -h, --help            show this help message and exit
>  --directory DIRECTORY
>                        Directory containing the .ped files. Default is the current directory.
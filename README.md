# Cross_Sectional_Analysis_of_Quantum_Specific_Code_Smells_in_Open_Source_Software_Communities_RP
Replication Package for the research project carried out in collaboration with SeSaLab.


## Goals
Two main dimensions are investigated: 
- the prevalence of individual quantum-specific code smells and their temporal evolution, and 
- the statistical associations between pairs of quantum-specific code smells and their temporal evolution. To this end, we employ the concepts of Prevalence and PrevalenceOdds Ratio (POR), which are widely used in cross-sectional studies to quantify occurrence rates and associations between categorical variables.

Based on these objectives, the study addresses the following research questions:
- RQ1: What is the prevalence of quantum-specific code smells in quantum software projects?
- RQ2: How does the prevalence of quantum-specific code smells evolve over time?
- RQ3: What relationships exist between different quantum-specific code smells?
- RQ4: How do the relationships between quantum-specific code smells evolve over time?

## Data Preparation
After a detailed analysis of the repositories, 90 repositories (out of a total of 286) were selected based on specific criteria (number of stars, contributors, etc.). This was done to avoid picking toy projects or small projects that were not useful for the applied study.

## Requirements
To replicate the study, you will need:
- Python 3.12+
- QSpire: Quantum-specific code smells detection tool developed by Dr. Alfieri

## RQ1 & RQ3
To answer RQ1 and RQ3, follow the steps listed below:
1. Download and install from the package QSmell and follow the instructions on README to install it.
2. Clone the projects in the file _dataset_quantum-enabled_projects_RQ1&RQ3.xlsx_
3. Run qspire using the following command
```{r}
qspire -static "path_folder_project" "path_folder_results"
```
4. Run the _counter.py_ script, located in the scripts folder, as follows:
```{r}
python -m counter.py --dataset ..\results\dataset_quantum_code_smells.xlsx
```
5. Run the script _correlationDetection.py_ as follows (pay attention to the path passed in the script!!!):
```{r}
python -m correlationDetection.py
```
Finally, PDF files will be available that graphically illustrate the results for RQ1 and RQ3.


## RQ2 & RQ4
The operational process for obtaining answers to RQ2 and RQ4 is very similar to the one seen previously, with the main difference being the creation and use of time slices.
The steps to be performed are listed below:
1. Clone the projects in the file _dataset_quantum-enabled_projects_RQ2&RQ4.xlsx_
2. Use the makeSlice.py script (create a GitHub token to avoid problems!!!) to divide the projects into different time slices, as follows:
```{r}
python -m makeSlice.py "repo_url" --token "personal_github_token"
```
3. Run qspire on each time slice using the following command:
```{r}
qspire -static "path_folder_project_sliced" "path_folder_results_sliced"
```
4. Run the _counter.py_ script, located in the scripts folder, as follows:
```{r}
python -m counter.py --dataset ..\results\dataset_quantum_code_smells_sliced.xlsx
```
5. Run the script _correlationDetection.py_ as follows (pay attention to the path passed in the script!!!):
```{r}
python -m correlationSlicedDetection.py
```
Finally, PDF files will be available that graphically illustrate the results for RQ2 and RQ4.

## Known Issues
1. If you have problems with opnepyxl installation, you should try to restart your PC. If it doesn't work I suggest using a Python virtual environment;



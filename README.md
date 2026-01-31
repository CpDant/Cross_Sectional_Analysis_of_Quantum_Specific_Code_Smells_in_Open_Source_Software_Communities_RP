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
1. Clone the repository [QSpire](https://github.com/Riccardoalfieri2003/Q-Spire)
2. Clone the projects in the file _dataset_quantum-enabled_projects_RQ1&RQ3.xlsx_
3. Run qspire using the following command
```{r}
qspire -static "path_folder_progetto" "path_folder_results"
```
4. In the folder where the tool output is saved (i.e., the one used in path_folder_results), run the _counter.py_ script, located in the scripts folder, as follows:
```{r}
python -m counter.py "path_folder_results" "path_folder_output_counter"
```
5. Save all results in an Excel file named _dataset_quantum_code_smells.xlsx_ and run the script _correlationDetection.py_ as follows (pay attention to the path passed in the script!!!):
```{r}
python -m correlationDetection.py
```
Finally, PDF files will be available that graphically illustrate the results for RQ1 and RQ3.


## RQ2 & RQ4
Il processo operativo per ottenere le risposte alla RQ2 e alla RQ4 è molto simile a quello visto in precedenza, la differenza sostanziale sta nella creazione e utilizzo delle slices temporali.
Di seguito sono elencati gli step da eseguire:
1. Effettuare il clone della repository [QSpire](https://github.com/Riccardoalfieri2003/Q-Spire)
2. Clonare i progetti presenti nel file _dataset_quantum-enabled_projects_RQ2&RQ4.xlsx_
3. Utilizzare lo script makeSlice.py (creare un token GitHub per evitare problemi!!!), per dividere i progetti in slices temporali differenti, in questo modo:
```{r}
python -m makeSlice.py "repo_url" --token "personal_github_token"
```
4. Run qspire on each time slice using the following command:
```{r}
qspire -static "path_folder_progetto_sliced" "path_folder_results_sliced"
```
5. In the folder where the tool output is saved (i.e., the one used in path_folder_results_sliced), run the _counter.py_ script, located in the scripts folder, as follows:
```{r}
python -m counter.py "path_folder_results" "path_folder_output_counter"
```
6. Save all results in an Excel file named _dataset_quantum_code_smells_sliced.xlsx_ and run the script _correlationDetection.py_ as follows (pay attention to the path passed in the script!!!):
```{r}
python -m correlationSlicedDetection.py
```
Alla fine si avranno a disposizione i file .pdf che illustrano graficamente i risultati relativi a RQ2 e RQ4.

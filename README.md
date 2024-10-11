# Facilitator of the local deployment of the EFSA Whole-Genome Sequencing One Health analytical pipeline

The European Food Safety Authority (EFSA) has recently defined the [“Guidelines for reporting Whole Genome Sequencing-based typing data through the EFSA One Health WGS System”](https://efsa.onlinelibrary.wiley.com/doi/10.2903/sp.efsa.2022.EN-7413), and released the EFSA One Health WGS analytical pipeline for the analysis of whole-genome sequencing (WGS) data of _Listeria monocytogenes_, _Salmonella enterica_ and _Escherichia coli_. This pipeline can be run through the EFSA One Health WGS System Portal (exclusively for the officially appointed users), but is also available for download through the following repository: https://dev.azure.com/efsa-devops/EFSA/_git/efsa.wgs.onehealth.

## Motivation

With the aim of facilitating the deployment of the EFSA One Health WGS analytical pipeline in local settings, we share an easy-to-use and surveillance-oriented script that: 

- allows providing **multiple samples** as input (**batch analysis**)
  
- **compiles the results of individual samples** into user- and surveillance-oriented **tabular reports**
 
- enables the integration of results of previous runs for routine genomic surveillance, i.e., can perform the **cumulative analysis** of growing datasets.

This implementation can be useful for laboratories that want to: i) implement the EFSA pipeline in their routine activities; ii) perform sample submission by programmatic access to the EFSA One Health WGS System; iii) perform pre-submission quality control to avoid uploading bad quality data to the EFSA portal; and iv) compare the results of the EFSA pipeline with their own routine surveillance pipelines. The tools available in the repository ["WGS_cluster_congruence"](https://github.com/insapathogenomics/WGS_cluster_congruence) can facilitate the later.

## Installation and dependencies
This script facilitates the deployment of the EFSA One Health WGS analytical pipeline but it does not substitutes this pipeline. Therefore, before installing everything that you need to run this script, **you must install the EFSA One Health WGS analytical pipeline following the instructions available at https://dev.azure.com/efsa-devops/EFSA/_git/efsa.wgs.onehealth**.

Briefly, you will need:
- A Linux computer or a Windows computer with WSL 
- Git - to clone the EFSA One Health WGS analytical workflow and the Docker repositories
- Docker - to build and then run the Docker images
- Conda - to install the environment with which you will run the script provided in this repository

_Note: EFSA One Health WGS analytical pipeline is a Nextflow workflow. The conda environment provided in this repository includes a Nextflow package. Therefore, you do not need to install it before._

**0. Install the EFSA One Health WGS analytical pipeline following the instructions available at https://dev.azure.com/efsa-devops/EFSA/_git/efsa.wgs.onehealth** (do not forget to properly setup the _nextflow.config_ for each species, including providing the right schema location)
  
**1. Navigate to the directory where you cloned the workflow, clone of this repository and install the conda environment:**
```
cd /PATH/TO/efsa.wgs.onehealth/
git clone https://github.com/insapathogenomics/cml_efsa.wgs.onehealth_facilitator.git
cd cml_efsa.wgs.onehealth_facilitator/
conda env create --name efsa_workflow --file=workflow_environment.yml
```

**2. Activate conda environment**
```
conda activate efsa_workflow
```

**3. Run the command line of the EFSA WGS One Health facilitator:**
```
python efsa_wgs_onehealth_facilitator.py -v
```

## Input

**Directory with paired-end Illumina FASTQ files** (sample names will be inferred from the FASTQ name until the first underscore "_")

OR

**Table in .tsv format with sample name and FASTQ location** (a template is provided in this repository)

*NOTE: Optionally, the directory of a previous run can be indicated for cumulative downstream analysis.*

## Output
- _alleles.tsv_ - **TSV file with the alleles** called in this run (and previous runs, if requested by the user) reported as CRC32 hash.
- _*_report.xlsx_ - Excel file with all the results of the run (and previous runs, if requested by the user), including a PASS/FAIL report, assembly metrics and extra typing data.
- _summary.tsv_ - TSV file with the summary results of the run, including the quality control PASS/FAIL information for each sample.
- _mlst.tsv_ - TSV file with the MLST information for each sample.
- _amr.tsv_ - TSV file with the AMR information for each sample.
- _pathotypes.tsv_ - TSV file with pathotyping information for each sample.

_NOTE: Each Excel sheet corresponds to the respective .tsv file. However, we are still providing the .tsv files so you can use them in downstream analysis._

## Folder structure
This script assumes the following folder structure for input/output files:
```
OUTPUT/ # Folder where the different runs are stored (it must already exist). In a surveillance scenario, it would correspond to the folder where all the runs of a given species are stored.
|___RUN1/ # Folder where the results of run1 are stored (it will be created by the script).
    |___alleles.tsv
    |___RUN1_report.xlsx
    |___summary.tsv
    |___mlst.tsv
    |___amr.tsv
    |___pathotypes.tsv
    |___Sample1/
        |___Sample1_R*.fastq.gz # Copy of the fastq files provided by the user.
        |___efsa_output/ # Folder with the results of EFSA pipeline. This folder will be created by EFSA pipeline and have a random name.
 ```
The directory with the fastq files or the template.tsv with all sample information can be placed anywhere in your computer. You just need to indicate the full path.
## Examples

In the _examples/_ folder we provide a set of public Illumina paired-end fastq files (retrieved from the public [BeONE](https://www.medrxiv.org/content/10.1101/2024.07.24.24310933v1) datasets) for _L. monocytogenes_, _S. enterica_ and _E.coli_ that can be used to try the script. Here, we provide command line examples for the _S. enterica_ data.

#### 1. Run the _efsa_wgs_onehealth_facilitator.py_ script on multiple samples:
 ```
python efsa_wgs_onehealth_facilitator.py -f examples/senterica/senterica_fastq_test1/ -o examples/senterica -r test1 -s 'salmonella enterica' -nf /FULL/PATH/TO/YOUR/nextflow.config
```

After running this example, you should have the following outputs:
```
senterica/
|___test1/
    |___alleles.tsv
    |___test1_report.xlsx
    |___summary.tsv
    |___mlst.tsv
    |___amr.tsv
    |___pathotypes.tsv
    |___ERR10441970/
        |___ERR10441970_*.fastq.gz
        |___folder_with_random_name/ # Folder with the results of EFSA pipeline. This folder will be created by EFSA pipeline and have a random name.
    |___ERR10441971/
        |___ERR10441971_*.fastq.gz
        |___folder_with_random_name/ # Folder with the results of EFSA pipeline. This folder will be created by EFSA pipeline and have a random name.
```

#### 2. Run the _efsa_wgs_onehealth_facilitator.py_ script on a single sample and requesting the merge of the results with a previous run:
 ```
python efsa_wgs_onehealth_facilitator.py -f examples/senterica/senterica_fastq_test1/ -o examples/senterica -r test2 -s 'salmonella enterica' -nf /FULL/PATH/TO/YOUR/nextflow.config --previous-run test1
```
This example can only be run after the previous run was completed. After running this example, you should have the following outputs:
```
senterica/
|___test1/
    |___alleles.tsv
    |___test1_report.xlsx
    |___summary.tsv
    |___mlst.tsv
    |___amr.tsv
    |___pathotypes.tsv
    |___ERR10441970/
        |___ERR10441970_*.fastq.gz
        |___efsa_folder_with_random_name/
    |___ERR10441971/
        |___ERR10441971_*.fastq.gz
        |___efsa_folder_with_random_name/
|___test2/
    |___alleles.tsv
    |___test2_report.xlsx
    |___summary.tsv
    |___mlst.tsv
    |___amr.tsv
    |___pathotypes.tsv
    |___ERR10441976/
        |___ERR10441976_*.fastq.gz
        |___efsa_folder_with_random_name/
```
_NOTE: All the reports provided in test2/, as well as the allele hash, have the cumulative results of test1 and test2 runs._

## Clustering analysis with [ReporTree](https://github.com/insapathogenomics/ReporTree)

The combined reports of this tool can be used for downstream clustering analysis using [ReporTree](https://github.com/insapathogenomics/ReporTree) following the cgMLST approach implemented in the [EFSA One Health WGS System](https://efsa.onlinelibrary.wiley.com/doi/10.2903/sp.efsa.2022.EN-7413), which relies on static cgMLST schemas available in https://chewbbaca.online. Here, we provide command line example that could be used to perform the clustering of the _S. enterica_ samples provided in _examples/_ using [ReporTree](https://github.com/insapathogenomics/ReporTree), as a downstream analysis of [example 2](https://github.com/vmixao/cml_efsa.wgs.onehealth_facilitator/edit/main/README.md#2-run-the-efsa_wgs_onehealth_facilitatorpy-script-on-a-single-sample-and-requesting-the-merge-of-the-results-with-a-previous-run):

```
python reportree.py 
```




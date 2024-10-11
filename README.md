# Facilitator of the local deployment of the EFSA Whole-Genome Sequencing One Health analytical pipeline

The European Food Safety Authority (EFSA) has recently defined the [“Guidelines for reporting Whole Genome Sequencing-based typing data through the EFSA One Health WGS System”](https://efsa.onlinelibrary.wiley.com/doi/10.2903/sp.efsa.2022.EN-7413), and released the EFSA One Health WGS analytical pipeline for the analysis of whole-genome sequencing (WGS) data of _Listeria monocytogenes_, _Salmonella enterica_ and _Escherichia coli_. This pipeline can be run through the EFSA One Health WGS System Portal (exclusively for the officially appointed users), but is also available for download through the following repository: https://dev.azure.com/efsa-devops/EFSA/_git/efsa.wgs.onehealth.

## Motivation

With the aim of facilitating the deployment of the EFSA One Health WGS analytical pipeline in local settings, we share an easy-to-use and surveillance-oriented script that: 

- allows providing **multiple samples** as input (**batch analysis**)
  
- **compiles the results of individual samples** into user- and surveillance-oriented **tabular reports**
 
- enables the integration of results of previous runs for routine genomic surveillance, i.e., can perform the **cumulative analysis** of growing datasets.

This implementation can be useful for laboratories that want to: i) implement the EFSA pipeline in their routine activities; ii) perform sample submission by programmatic access to the EFSA One Health WGS System; iii) perform pre-submission quality control to avoid uploading bad quality data to the EFSA portal; and iv) compare the results of the EFSA pipeline with their own routine surveillance pipelines. The tools available in the repository ["WGS_cluster_congruence"](https://github.com/insapathogenomics/WGS_cluster_congruence) can facilitate the later.

## Input

**Directory with paired-end Illumina FASTQ files** (sample names will be inferred from FASTQ name until the first underscore "_")

OR

**Table in .tsv format with sample name and FASTQ location** (template is provided)

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

## Clustering analysis with [ReporTree](https://github.com/insapathogenomics/ReporTree)

The combined reports of this tool can be used for downstream clustering analysis using [ReporTree](https://github.com/insapathogenomics/ReporTree) following the cgMLST approach implemented in the [EFSA One Health WGS System]((https://efsa.onlinelibrary.wiley.com/doi/10.2903/sp.efsa.2022.EN-7413), which relies on static cgMLST schemas available in https://chewbbaca.online. 

Example of ReporTree run:

    $ 

List of schemas accepted by the EFSA One Health WGS system

## Installation and dependencies



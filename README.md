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

## Main Output
- _alleles.tsv_ - **TSV file with the alleles** called in this run (and previous runs, if requested by the user) reported as CRC32 hash.
- _*_report.xlsx_ - Excel file with all the results of the run (and previous runs, if requested by the user), including a PASS/FAIL report, assembly metrics and extra typing data.
- _summary.tsv_ - TSV file with the summary results of the run, including the quality control PASS/FAIL information for each sample.
- _mlst.tsv_ - TSV file with the MLST information for each sample.
- _amr.tsv_ - TSV file with the AMR information for each sample.
- _pathotypes.tsv_ - TSV file with pathotyping information for each sample.

_NOTE: Each Excel sheet corresponds to the respective .tsv file. However, we are still providing the .tsv files so you can use them in downstream analysis._

## Examples

In the _examples/_ folder we provide a set of public Illumina paired-end fastq files (retrieved from the public BeONE datasets) for _L. monocytogenes_, _S. enterica_ and _E.coli_.
## Clustering analysis with [ReporTree](https://github.com/insapathogenomics/ReporTree)

The combined reports of this tool can be used for downstream clustering analysis using [ReporTree](https://github.com/insapathogenomics/ReporTree) following the cgMLST approach implemented in the [EFSA One Health WGS System]((https://efsa.onlinelibrary.wiley.com/doi/10.2903/sp.efsa.2022.EN-7413), which relies on static cgMLST schemas available in https://chewbbaca.online. 

Example of ReporTree run:

    $ 

List of schemas accepted by the EFSA One Health WGS system

## Installation and dependencies



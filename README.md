# Facilitator of the local deployment of the EFSA's Whole Genome Sequencing OneHealth analytical pipeline

The European Food Safety Authority (EFSA) has recently defined [“Guidelines for reporting Whole Genome Sequencing-based typing data through the EFSA One Health WGS System”](https://efsa.onlinelibrary.wiley.com/doi/10.2903/sp.efsa.2022.EN-7413), and released the EFSA One Health WGS analytical pipeline for the analysis of whole-genome sequencing (WGS) data of Salmonella enterica, Listeria monocytogenes and Escherichia coli. This pipeline can be run through the EFSA One Health WGS System Portal (exclusively for the officially appointed users), but is also available for download through the following repository: https://dev.azure.com/efsa-devops/EFSA/_git/efsa.wgs.onehealth.

## Motivation

Facilitate the deployment of the EFSA's Whole Genome Sequencing OneHealth analytical pipeline in a local setting through an easy-to-use and surveillance-oriented script that: 

- allows **multiple samples** as input (**batch analysis**)
  
- **compiles the results of individual samples** into user- and surveillance-oriented **tabular reports**
 
- enables the integration of results of previous runs for routine genomic surveillance, i.e., **cumulative analysis** of growing datasets.

This implementation can be useful for laboratories that want to: i) implement the EFSA pipeline in their routine activities; ii) perform sample submission by programmatic access to the EFSA One Health WGS System; iii) perform pre-submission quality control to avoid uploading bad quality data to the EFSA portal; and iv) compare the results of the EFSA pipeline with their own routine surveillance pipelines. The tools available in the repository ["WGS_cluster_congruence"](https://github.com/insapathogenomics/WGS_cluster_congruence) can facilitate the later.

## Input

**Directory with paired-end Illumina FASTQ files** (sample names will be inferred from FASTQ name until the first underscore "_")

OR

**Table in .tsv format with sample name and FASTQ location** (template is provided)

*NOTE: Optionally, the allelic matrix and/or pipeline reports from a previous run can be provided for cumulative downstream analysis.*

## Main Output

**Pipeline results** (report of individual pipeline steps, including a PASS/FAIL report, assembly metrics and extra typing data, when applicable)

AND

**Allelic matrix** (alleles reported as CRC32 hash) 

## Clustering analysis with [ReporTree](https://github.com/insapathogenomics/ReporTree)

The combined reports of this tool can be used for downstream clustering analysis using [ReporTree](https://github.com/insapathogenomics/ReporTree) following the cgMLST approach implemented in the [EFSA One Health WGS System]((https://efsa.onlinelibrary.wiley.com/doi/10.2903/sp.efsa.2022.EN-7413), which relies on static cgMLST schemas available in https://chewbbaca.online. 

Example of ReporTree run:

    $ 

List of schemas accepted by the EFSA One Health WGS system

## Installation and dependencies



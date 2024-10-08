# Facilitator of the local deployment of the EFSA's Whole Genome Sequencing OneHealth analytical pipeline

The European Food Safety Authority (EFSA) has recently defined “Guidelines for reporting Whole Genome Sequencing-based typing data through the EFSA One Health WGS System” (https://efsa.onlinelibrary.wiley.com/doi/10.2903/sp.efsa.2022.EN-7413), and released the EFSA One Health WGS analytical pipeline for the analysis of whole-genome sequencing (WGS) data of Salmonella enterica, Listeria monocytogenes and Escherichia coli. This pipeline can be run through the EFSA One Health WGS System Portal (exclusively for the officially appointed users), but is also available for download through the following repository: https://dev.azure.com/efsa-devops/EFSA/_git/efsa.wgs.onehealth.

This repository contains a surveillance-oriented script that facilitates the local deployment of the EFSA's Whole Genome Sequencing OneHealth analytical pipeline by:

- allowing multiple samples (paired-end Illumina FASTQ) as input (**batch analysis**)
- compiling the results of individual samples into two user- and surveillance-oriented **tabular reports**:  
                1. **allelic matrix** (alleles reported as CRC32 hash)  
                2. **pipeline results** (report of individual pipeline steps) 
- enabling the integration of results of previous runs for routine genomic surveillance (i.e., cumulative analysis of growing datasets)



#!/usr/bin/env	python3

"""
This script was designed to help you run the EFSA command line pipeline

@INSAPathoGenomics
"""

import sys
import os
import argparse
import textwrap
import glob
import datetime as datetime
import pandas
from efsa_parser import EfsaResults

version = "1.0.0b"
last_updated = "2024-10-10"

script_location = os.path.realpath(__file__)
script_path = script_location.rsplit("/", 2)[0]
efsa_workflow = script_path + "/onehealth.nf"
python = sys.executable

# functions ----------

def distribute_fastq(fastq_directory, samples_info, outdir):
	""" This function distributes the different fastq files into separate directories """

	sample_dirs = []
	sample_names = {}
	
	if fastq_directory != "":
		for filename in glob.glob(fastq_directory + "/*"):
			if "/" in filename:
				filename = filename.split("/")[-1]
			sample = filename.split("_")[0]
			sample_dir = outdir + "/" + sample
			if sample_dir not in sample_dirs:
				sample_dirs.append(sample_dir)
				sample_names[sample_dir] = sample
				os.system("mkdir " + sample_dir)
			os.system("cp " + fastq_directory + "/" + sample + "* " + sample_dir)
	elif samples_info != "":
		with open(samples_info) as infile:
			lines = infile.readlines()
			for line in lines:
				lin = line.split("\n")[0]
				l = lin.split("\t")
				sample = l[0]
				fq1 = l[1]
				fq2 = l[2]
				sample_dir = outdir + "/" + sample
				if sample_dir not in sample_dirs:
					sample_dirs.append(sample_dir)
					sample_names[sample_dir] = sample
					os.system("mkdir " + sample_dir)
				os.system("cp " + fq1 + " " + sample_dir)
				os.system("cp " + fq2 + " " + sample_dir)
   
	return sample_dirs, sample_names

def run_efsa_pipeline(sample_dir, nextflow_config, species):
    """ This function runs the EFSA command line pipeline """

    cmd = "cd " + sample_dir + "; nextflow -C '" + nextflow_config + "' run " + efsa_workflow + " --readType='dual' --species='" + species + "' --indir '.' --outdir '.'; cd ../../.."
    print("\tRunning EFSA pipeline with the following command:\n\t",cmd,"\n")
    returned_value = os.system(cmd)

    return returned_value

def join_df(old_df,new_df):
	""" This function joins two dataframes
	input: pandas dataframe
	output: pandas dataframe
	"""
	
	old_df.set_index(old_df.columns[0], inplace = True)
	new_df.set_index(new_df.columns[0], inplace = True)
	final_df = pandas.concat([old_df, new_df])
	final_df = final_df.reset_index()

	return final_df
	
def join_allele_matrices(sample_dirs, previous_run):
	""" This function joins all allele matrices  """
	
	if previous_run != "":
		df = pandas.read_table(previous_run + "/alleles.tsv", dtype=str)
	else:
		df = pandas.DataFrame()

	for directory in sample_dirs:
		counter = 0
		for filename in glob.glob(directory + "/*/_hashed_results.tsv"):
			counter += 1
		if counter == 0:
			print("\tNo allele hash file found for " + directory)
		elif counter > 1:
			print("\tMultiple allele hash files found for the same sample... please check run outputs for " + directory)
		else:
			if len(df.columns) == 0:
				df = pandas.read_table(filename, dtype=str)
				df[df.columns[0]][0] = df[df.columns[0]][0].split("_contigs.fa")[0]
			else:
				new_df = pandas.read_table(filename, dtype = str)
				new_df[new_df.columns[0]][0] = new_df[new_df.columns[0]][0].split("_contigs.fa")[0]
				if len(set(df.columns) - set(new_df.columns)) == 0 and len(set(new_df.columns) - set(df.columns)) == 0:
					if new_df[new_df.columns[0]][0] not in df[df.columns[0]].values.tolist():
						df = join_df(df,new_df)
					else:
						sys.exit(str(new_df[new_df.columns[0]][0]) + " was already present in the previous table! Cannot proceed!")
				else:
					sys.exit("Column names do not match between the different files! Cannot proceed!")
	
	return df

def join_reports_efsa_parser(out_dir, sample_dirs, run_name):
	""" This function joins the reports of a given run with the efsa parser """
	
	dir_to_sample = {}
	failed = {}
	for directory in sample_dirs:
		counter = 0
		sample_name = directory.split("/")[-1]
		for filename in glob.glob(directory + "/*/_parseresults.json"):
			sample_run = filename.split("/")[-2]
			sample_dir = directory + "/" + sample_run
			counter += 1
		if counter == 1:
			dir_to_sample[sample_name] = sample_dir
		elif counter == 0:
			failed[sample_name] = directory

	if len(dir_to_sample.keys()) > 0:
		output_file = out_dir + "/" + run_name + "/" + run_name + "_report.xlsx"
		outputs_directory = out_dir + "/" + run_name
		results = EfsaResults(dir_to_sample, outputs_directory, output_file)
		results.parse_all_results()
		results.merge_output()
		run_successful_samples = True
	else:
		run_successful_samples = False

	return failed, run_successful_samples

def prepare_final_reports(out_dir, run_name, failed, previous_run, run_successful_samples):
	""" This function adds QC information to the summary report """

	passed_qc = []
	failed_df_tsv = {}
	failed_df_tsv["Analysis_ID"] = []
	failed_df_tsv["QC_VOTE"] = []

	if len(failed) > 0:
		for sample in failed.keys():
			for filename in glob.glob(failed[sample] + "/*/_logging.json"):
				with open(filename) as log_info:
					lines = log_info.readlines()
					for line in lines:
						if "title" in line:
							info = line.split("\"title\": \"")[1]
							error = info.split("\"")[0]
							failed_df_tsv["Analysis_ID"].append(sample)
							failed_df_tsv["QC_VOTE"].append(error)
		failed_df_tsv = pandas.DataFrame(failed_df_tsv)
	else:
		failed_df_tsv = pandas.DataFrame()

	if run_successful_samples:
		summary_tsv = pandas.read_table(out_dir + "/" + run_name + "/summary.tsv")
		mlst_tsv = pandas.read_table(out_dir + "/" + run_name + "/mlst.tsv")
		try:
			amr_tsv = pandas.read_table(out_dir + "/" + run_name + "/amr.tsv")
		except pandas.errors.EmptyDataError:
			amr_tsv = pandas.DataFrame()
		try:
			pathotyping_tsv = pandas.read_table(out_dir + "/" + run_name + "/pathotypes.tsv")
		except pandas.errors.EmptyDataError:
			pathotyping_tsv = pandas.DataFrame()
		
		for sample in summary_tsv["Analysis_ID"].values.tolist():
			passed_qc.append("PASS")
		summary_tsv.insert(1, "QC_VOTE", passed_qc)
		summary_tsv = join_df(summary_tsv, failed_df_tsv)

	else:
		summary_tsv = failed_df_tsv
		mlst_tsv = pandas.DataFrame()
		amr_tsv = pandas.DataFrame()
		pathotyping_tsv = pandas.DataFrame()

	if previous_run != "":
		previous_summary = pandas.read_table(previous_run + "/summary.tsv")
		final_summary = join_df(previous_summary, summary_tsv)
		try:
			previous_mlst = pandas.read_table(previous_run + "/mlst.tsv")
			if mlst_tsv.empty:
				final_mlst = previous_mlst
			else:
				final_mlst = join_df(previous_mlst, mlst_tsv)
		except pandas.errors.EmptyDataError:
			final_mlst = mlst_tsv
		try:
			previous_amr = pandas.read_table(previous_run + "/amr.tsv")
			if amr_tsv.empty:
				final_amr = previous_amr
			else:
				final_amr = join_df(previous_amr, amr_tsv)
		except pandas.errors.EmptyDataError:
			final_amr = amr_tsv
		try:
			previous_pathotyping = pandas.read_table(previous_run + "/pathotypes.tsv")
			if pathotyping_tsv.empty:
				final_pathotyping = previous_pathotyping
			else:
				final_pathotyping = join_df(previous_pathotyping, pathotyping_tsv)
		except pandas.errors.EmptyDataError:
			final_pathotyping = pathotyping_tsv
	else:
		final_summary = summary_tsv
		final_mlst = mlst_tsv
		final_amr = amr_tsv
		final_pathotyping = pathotyping_tsv
	
	final_summary.to_csv(out_dir + "/" + run_name + "/summary.tsv", index = False, header=True, sep ="\t")
	final_mlst.to_csv(out_dir + "/" + run_name + "/mlst.tsv", index = False, header=True, sep ="\t")
	final_amr.to_csv(out_dir + "/" + run_name + "/amr.tsv", index = False, header=True, sep ="\t")
	final_pathotyping.to_csv(out_dir + "/" + run_name + "/pathotypes.tsv", index = False, header=True, sep ="\t")

	with pandas.ExcelWriter(out_dir + "/" + run_name + "/" + run_name + "_report.xlsx") as writer:
		final_summary.to_excel(writer, sheet_name = "Summary", index = False)
		final_mlst.to_excel(writer, sheet_name = "MLST", index = False)
		final_amr.to_excel(writer, sheet_name = "AMR", index = False)
		final_pathotyping.to_excel(writer, sheet_name = "Pathotypes", index = False)
		
def read_json_efsa(report_file, strain):
	""" This function converts EFSA json report into a pandas dataframe
	input: filename
	output: dataframe
	"""
	
	info_mx = {}
	info_mx["sample"] = strain
	order = []
	order.append("sample")
	checked = {}
	with open(report_file) as infile:
		f = infile.readlines()
		for line in f:
			l = line.split("\n")[0]
			info = l.split(",")
			for i in info:
				if "{" in i:
					i = i.split("{")[-1]
				if "}" in i:
					i = i.split("}")[0]
				if len(i.split(": ")) == 2:
					k,v = i.split(": ")
					if "\"" in k:
						k = k.split("\"")[1]
					if "\"" in v:
						v = v.split("\"")[1]
					if k not in checked.keys():
						checked[k] = 0
					else:
						checked[k] += 1
					if checked[k] == 0:
						k = k
					else:
						k = k + "_" + str(checked[k])
					order.append(k)
					info_mx[k] = v
					
	mx = pandas.DataFrame(data = info_mx, columns=order, index=[strain])
	
	return mx

# running the pipeline	----------

def main():
    
	# argument options	----------
    
	parser = argparse.ArgumentParser(prog="efsa_wgs_onehealth_facilitator.py", formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent("""\
									###############################################################################             
									#                                                                             #
									#                     efsa_wgs_onehealth_facilitator.py                       #
									#                                                                             #
									############################################################################### 
									                            
									This script is intended to facilitate the deployment of the EFSA's Whole Genome
									Sequencing OneHealth analytical pipeline in a local setting through an 
									easy-to-use and surveillance-oriented script that:
										1. allows multiple samples as input (batch analysis)
										2. compiles the results of individual samples into user- and 
										   surveillance-oriented tabular reports
										3. enables the integration of results of previous runs for routine 
										   genomic surveillance, i.e., cumulative analysis of growing datasets.
									-------------------------------------------------------------------------------"""))
	
	## general parameters
	
	versioning = parser.add_argument_group("Version", "efsa_wgs_onehealth_facilitator.py")
	versioning.add_argument("-v", "--version", dest="version", action="store_true", help="Print version and exit")
	
	group0 = parser.add_argument_group("Input/Output", "Input/Output specifications")
	group0.add_argument("-f", "--fastq", dest="fastq", default="", type=str, help="Directory with the fastq files for this run. Sample names will be \
						inferred from the FASTQ name until the first underscore '_'. This argument is mandatory if no '--sample-info' is provided.")
	group0.add_argument("-samples", "--samples", dest="sample_info", default="", type=str, help="TSV file with the indication of sample name and the \
						complete PATH to fastq1 and fastq2 (sample\tfq1\tfq2). This argument is mandatory, if no '--fastq' is provided. Please note that \
						no header is expected and sample names can follow any format as far as they do not have blank spaces ' '.")
	group0.add_argument("-o", "--output", dest="output", default="", type=str, help="[MANDATORY] Directory where the results of each run are stored. Please \
						do not include a final slash '/' in the directory name.")
	group0.add_argument("-r", "--run", dest="run_name", default="run_efsa", type=str, help="Name of the run (default: run_efsa).")
	group0.add_argument("-s", "--species", dest="species", default="", type=str, help="[MANDATORY] Species name between quotation marks (currently only \
					 	available for: 'listeria monocytogenes', 'salmonella enterica' and 'escherichia coli'). Please indicate the name of the species \
						between quotation marks.")
	group0.add_argument("-nf", "--nextflow-config", dest="nextflow_config", default="", type=str, help="[MANDATORY] Full PATH to the nextflow config.")
	group0.add_argument("--previous-run", dest="previous_run", default="", type=str, help="Full path to a previous run (the reports of the present run \
					 	will be added to the reports of this previous run). Please do not include a final slash '/' in the directory name.")
	
	args = parser.parse_args()

	# check if version	----------
	
	if args.version:
		print("version:", version, "\nlast_updated:", last_updated)
		sys.exit()
	
	if args.fastq == "" and args.sample_info == "":
		sys.exit("Please indicate a valid fastq folder or provide a tsv file with sample information!")
	elif args.fastq != "" and args.sample_info != "":
		sys.exit("You indicated a fastq folder and provides a tsv file with sample information. I am confused and do not know which one to use!")
	if args.output == "":
		sys.exit("Please indicate a valid output folder!")
	if args.species != "listeria monocytogenes" and args.species != "salmonella enterica" and args.species != "escherichia coli":
		sys.exit("Please indicate a valid species!")
	if args.nextflow_config == "":
		sys.exit("Please indicate a valid nextflow config!")
	
	if os.path.exists(args.output + "/" + args.run_name):
		sys.exit("There is another run with the same name... I cannot proceed :-( please remove the previous run or choose a different run name!")
	
	print("\n******************** running_efsa_pipeline.py ********************\n")
	print("version " + str(version) + " last updated on " + str(last_updated) + "\n")
	print(" ".join(sys.argv))
	
	start = datetime.datetime.now()
	print("start: " + str(start))
	
	print("\nCreating the run directory...")
	os.system("mkdir " + args.output + "/" + args.run_name)
	sample_dirs, sample_names = distribute_fastq(args.fastq, args.sample_info, args.output + "/" + args.run_name)
	
	print("\nRunning EFSA pipeline...")
	for directory in sample_dirs:
		run_status = run_efsa_pipeline(directory, args.nextflow_config, args.species)
	
	print("\nMerging allele matrices...")
	allele_matrix = join_allele_matrices(sample_dirs, args.previous_run)
	allele_matrix.to_csv(args.output + "/" + args.run_name + "/alleles.tsv", index = False, header=True, sep ="\t")
	
	print("\nMerging reports...")
	
	failed, run_successful_samples = join_reports_efsa_parser(args.output, sample_dirs, args.run_name)
	prepare_final_reports(args.output, args.run_name, failed, args.previous_run, run_successful_samples)

	end = datetime.datetime.now()
	elapsed = end - start
	print("\n------------------------------------------------------------\n")
	print("Done!\n")
	print("\nEnd: " + str(end))
	print("Time elapsed: " + str(elapsed))

if __name__ == "__main__":
    main()
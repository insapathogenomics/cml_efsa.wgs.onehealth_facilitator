import json
import os

from typing import List, Optional

import os
import pandas as pd


def recursive_parse_json(json_dict, added_dict={}) -> dict:
    """
    given a dictionary, return a dictionary of the last key and value pairs in the dictionary
    """
    if isinstance(json_dict, dict):
        for key, value in json_dict.items():
            if isinstance(value, dict):
                recursive_parse_json(value, added_dict)
            else:
                added_dict[key] = value

    return added_dict


def find_efsa_output(sample_dir: str) -> str:
    """
    Find the efsa output directory in the sample directory
    """
    for root, dirs, files in os.walk(sample_dir):
        for dir in dirs:
            if not dir.startswith("work"):
                return os.path.join(root, dir)
    return None


def find_all_efsa_outptus(efsa_output_directoy: str) -> dict:
    """
    Find all efsa output directories in the efsa output directory"""

    efsa_outputs = os.listdir(efsa_output_directoy)
    efsa_outputs = {
        output: os.path.join(efsa_output_directoy, output) for output in efsa_outputs
    }
    efsa_outputs = {
        output: find_efsa_output(efsa_outputs[output]) for output in efsa_outputs
    }

    empty_outputs = [output for output in efsa_outputs if efsa_outputs[output] is None]
    efsa_outputs = {
        output: efsa_outputs[output]
        for output in efsa_outputs
        if output not in empty_outputs
    }

    return efsa_outputs, empty_outputs


class JsonParser:

    def __init__(self, json_file):

        self.parsed_results = json_file

    def get_parsed_results(self):
        try:
            with open(self.parsed_results) as f:
                results = json.load(f)
            return results
        except FileNotFoundError:

            return {}

    @staticmethod
    def parse_section_return_dict(json_dict):
        return json_dict

    @staticmethod
    def parse_unspecified_section(json_dict) -> dict:
        return recursive_parse_json(json_dict)


class EfsaParser:
    quality_check_sections = ["QualityCheck", "Results"]
    output_efsa = "_parseresults.json"

    def __init__(self, output_directory, analysis_id: Optional[str] = None) -> None:

        if not analysis_id:
            self.analysis_id = os.path.basename(output_directory)
        else:
            self.analysis_id = analysis_id
        self.gene_profiles = {}
        self.summary = {"Analysis_ID": self.analysis_id}
        self.output_directory = output_directory
        self.parser = JsonParser(os.path.join(self.output_directory, self.output_efsa))

        self.section_process_dict = {
            "Fastp": JsonParser.parse_section_return_dict,
            "ContaminationCheck": JsonParser.parse_unspecified_section,
            "AssemblyQualityStatistics": JsonParser.parse_unspecified_section,
            "cgMLSTQC": JsonParser.parse_section_return_dict,
            "SpeciesDetermination": JsonParser.parse_section_return_dict,
            "PredictedSerotype": self.serotype_parser,
            "PredictedPathotype": self.parse_pathotype_section,
            "AMRProfile": self.parse_amr_profile_section,
            "MLSTSequenceType": self.parse_mlst_section,
        }

    @staticmethod
    def serotype_parser(json_dict: dict):
        try:
            return {
                "Serotype": json_dict["Serotype"],
                "SerotypePrediction_Software": json_dict["Software"],
            }
        except KeyError:
            return {}

    def parse_pathotype_section(self, json_dict: dict):

        self.gene_profiles["PredictedPathotype"] = json_dict["GeneList"]

        json_dict.pop("GeneList")
        json_parsed = JsonParser.parse_unspecified_section(json_dict)
        json_parsed["PathotypePrediction_Software"] = json_dict["Software"]
        json_parsed.pop("Software")

        return json_parsed

    def parse_amr_profile_section(self, json_dict: dict):
        self.gene_profiles["AMRProfile"] = json_dict["seq_variations"]
        json_dict.pop("seq_variations")

        json_dict.pop("GeneList")
        json_dict["AMRProfile_Software"] = json_dict["Software"]
        json_dict.pop("Software")

        return json_dict

    def parse_mlst_section(self, json_dict: dict):
        self.gene_profiles["MLSTProfile"] = json_dict["GeneList"]
        json_dict.pop("GeneList")

        json_dict["MLSTProfile_Software"] = json_dict["Software"]
        json_dict.pop("Software")

        return json_dict

    def recursive_parse_json(self, json_dict):

        for subsection, value in json_dict.items():

            if not type(value) == dict:
                self.summary[subsection] = value
            elif subsection in self.section_process_dict:
                self.summary.update(self.section_process_dict[subsection](value))
            else:
                self.recursive_parse_json(value)

    ##############################################################
    ############ DEPLOY PARSERS TO MAIN SECTIONS ############

    def parse_json_results(self, parsed_results: dict):

        if not parsed_results:

            for section in self.quality_check_sections:
                self.summary[section] = "-"

            return

        for section in self.quality_check_sections:
            self.recursive_parse_json(parsed_results[section])

    ##############################################################
    ############ PROCESSING OF RESULTS INTO DATAFRAMES ############

    def process_summary(self):
        """join list values in summary dictionary to strings"""
        for key, value in self.summary.items():
            if isinstance(value, list):
                self.summary[key] = ", ".join(value)

    def summary_to_df(self):
        self.process_summary()

        summary_df = pd.DataFrame([self.summary])

        return summary_df

    def pathotype_dict_to_df(self):

        if "PredictedPathotype" not in self.gene_profiles:
            return pd.DataFrame()

        pathotype_df = pd.DataFrame(self.gene_profiles["PredictedPathotype"])
        pathotype_df["Analysis_ID"] = self.analysis_id

        return pathotype_df

    def amr_dict_to_df(self):

        if "AMRProfile" not in self.gene_profiles:
            return pd.DataFrame()

        amr_df = []

        for genevar in self.gene_profiles["AMRProfile"]:
            for item, values in genevar.items():
                values["Gene"] = values["genes"][0]
                values.pop("genes")
                values["phenotypes"] = ", ".join(values["phenotypes"])
                if values["phenotypes"] == "":
                    values["phenotypes"] = "-"

                amr_df.append(values)

        amr_df = pd.DataFrame(amr_df)
        amr_df["Analysis_ID"] = self.analysis_id

        # column id as first column
        cols = amr_df.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        amr_df = amr_df[cols]

        return amr_df

    def process_mlst_profile(self):

        if "MLSTProfile" not in self.gene_profiles:
            return pd.DataFrame()

        mlst_df = [
            {gene: st for gene, st in self.gene_profiles["MLSTProfile"][0].items()}
        ]

        mlst_df = pd.DataFrame(mlst_df)

        mlst_df["Analysis_ID"] = self.analysis_id

        mlst_df = mlst_df[[mlst_df.columns[-1]] + list(mlst_df.columns[:-1])]

        return mlst_df


class EfsaResults:

    SUMMARY_SHEET_NAME = "Summary"
    PATHOTYPES_SHEET_NAME = "Pathotypes"
    AMR_SHEET_NAME = "AMR"
    MLST_SHEET_NAME = "MLST"

    def __init__(
        self,
        dir_to_sample: dict,
        outputs_directory: str,
        output_file: str,
        log: bool = False,
    ) -> None:
        self.dir_to_sample = dir_to_sample
        self.outputs_directory = outputs_directory
        self.output_file = os.path.join(outputs_directory, output_file)
        self.parsed_results: List[EfsaParser] = []
        self.log = log

    def merge_dataframes(self, dataframes: list) -> pd.DataFrame:

        dataframes_to_dicts = [df.to_dict(orient="records") for df in dataframes]
        merged_list = [item for sublist in dataframes_to_dicts for item in sublist]
        merged_df = pd.DataFrame(merged_list)

        return merged_df

    def parse_all_results(self):
        for sample, directory in self.dir_to_sample.items():
            if self.log:
                print(f"Processing {sample}")
            parser = EfsaParser(directory, sample)
            json_results = parser.parser.get_parsed_results()
            if not json_results and self.log:
                print(f"No results found for {sample}")
            parser.parse_json_results(json_results)
            parser.process_summary()
            self.parsed_results.append(parser)

    def merge_summaries(self):
        summary_dfs = [parser.summary_to_df() for parser in self.parsed_results]
        merged_df = self.merge_dataframes(summary_dfs)

        return merged_df

    def merge_pathotypes(self):
        pathotype_dfs = [
            parser.pathotype_dict_to_df() for parser in self.parsed_results
        ]
        merged_df = self.merge_dataframes(pathotype_dfs)

        return merged_df

    def merge_amr_profiles(self):
        amr_dfs = [parser.amr_dict_to_df() for parser in self.parsed_results]
        merged_df = self.merge_dataframes(amr_dfs)

        return merged_df

    def merge_mlst_profiles(self):
        mlst_dfs = [parser.process_mlst_profile() for parser in self.parsed_results]
        merged_df = self.merge_dataframes(mlst_dfs)

        return merged_df

    def check_output_file(self):

        if os.path.exists(self.output_file):

            with pd.ExcelFile(self.output_file) as reader:
                if all(
                    sheet in reader.sheet_names
                    for sheet in [
                        self.SUMMARY_SHEET_NAME,
                        self.PATHOTYPES_SHEET_NAME,
                        self.AMR_SHEET_NAME,
                        self.MLST_SHEET_NAME,
                    ]
                ):
                    return True
                else:
                    return False
        else:
            return False

    def extract_existing_output(self):

        with pd.ExcelFile(self.output_file) as reader:
            summary_df = pd.read_excel(reader, sheet_name=self.SUMMARY_SHEET_NAME)
            pathotype_df = pd.read_excel(reader, sheet_name=self.PATHOTYPES_SHEET_NAME)
            amr_df = pd.read_excel(reader, sheet_name=self.AMR_SHEET_NAME)
            mlst_df = pd.read_excel(reader, sheet_name=self.MLST_SHEET_NAME)

        return summary_df, pathotype_df, amr_df, mlst_df

    def merge_output_with_existing(self):

        summary_df, pathotype_df, amr_df, mlst_df = self.extract_existing_output()

        new_summary_df = self.merge_summaries()
        new_pathotype_df = self.merge_pathotypes()
        new_amr_df = self.merge_amr_profiles()
        new_mlst_df = self.merge_mlst_profiles()

        summary_df = self.merge_dataframes([summary_df, new_summary_df])
        pathotype_df = self.merge_dataframes([pathotype_df, new_pathotype_df])
        amr_df = self.merge_dataframes([amr_df, new_amr_df])
        mlst_df = self.merge_dataframes([mlst_df, new_mlst_df])

        return summary_df, pathotype_df, amr_df, mlst_df

    def compound_output(self):

        if self.check_output_file():
            summary_df, pathotype_df, amr_df, mlst_df = (
                self.merge_output_with_existing()
            )
        else:
            summary_df = self.merge_summaries()
            pathotype_df = self.merge_pathotypes()
            amr_df = self.merge_amr_profiles()
            mlst_df = self.merge_mlst_profiles()

        return summary_df, pathotype_df, amr_df, mlst_df

    @staticmethod
    def process_df(dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe.fillna("-", inplace=True)
        # drop duplicates using Analysis_ID
        dataframe = dataframe.drop_duplicates().reset_index(drop=True)
        return dataframe

    def process_output(self):

        summary_df, pathotype_df, amr_df, mlst_df = self.compound_output()

        summary_df = self.process_df(summary_df)
        pathotype_df = self.process_df(pathotype_df)
        amr_df = self.process_df(amr_df)
        mlst_df = self.process_df(mlst_df)

        if "ST" in summary_df.columns:

            # match from sample to mlst_df
            mlst_df = mlst_df.merge(
                summary_df[["Analysis_ID", "ST"]], on="Analysis_ID", how="left"
            )

            mlst_df = mlst_df[["Analysis_ID", "ST"] + list(mlst_df.columns[1:-1])]

        return summary_df, pathotype_df, amr_df, mlst_df

    def merge_output(self):

        summary_df, pathotype_df, amr_df, mlst_df = self.process_output()

        os.makedirs(self.outputs_directory, exist_ok=True)

        with pd.ExcelWriter(self.output_file) as writer:
            summary_df.to_excel(writer, sheet_name=self.SUMMARY_SHEET_NAME, index=False)
            pathotype_df.to_excel(
                writer, sheet_name=self.PATHOTYPES_SHEET_NAME, index=False
            )
            amr_df.to_excel(writer, sheet_name=self.AMR_SHEET_NAME, index=False)
            mlst_df.to_excel(writer, sheet_name=self.MLST_SHEET_NAME, index=False)

        summary_df.to_csv(
            os.path.join(self.outputs_directory, "summary.tsv"), sep="\t", index=False
        )

        pathotype_df.to_csv(
            os.path.join(self.outputs_directory, "pathotypes.tsv"),
            sep="\t",
            index=False,
        )

        amr_df.to_csv(
            os.path.join(self.outputs_directory, "amr.tsv"), sep="\t", index=False
        )

        mlst_df.to_csv(
            os.path.join(self.outputs_directory, "mlst.tsv"), sep="\t", index=False
        )

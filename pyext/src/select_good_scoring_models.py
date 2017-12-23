
import IMP
import GoodScoringModelSelector
import os,sys,string,math
import argparse

def parse_args():
    
    parser = argparse.ArgumentParser(description="List and extract good-scoring models from a set of sampling runs. Example of usage: select_good_scoring_models.py -rd <run_directory_for_sampling> -rp <run_prefix> -sl ExcludedVolumeSphere_None GaussianEMRestraint_None -pl CrossLinkingMassSpectrometryDataScore|XLDSS CrossLinkingMassSpectrometryDataScore|XLEDC -agl -9999999.0 -99999.0 -aul 99999999.0 999999.0 -mlt 0 0 -mut 0 0. Flag -h for more details.")
    
    parser.add_argument("-rd","--run_directory",dest="run_dir",help="directory in which sampling results are stored") 
    
    parser.add_argument("-rp","--run_prefix",dest="run_prefix",help="prefix of runs") 
                        
    parser.add_argument("-sl","--selection_keywords_list",nargs='+',type=str,dest="selection_keywords_list",help="list of stat file keywords corresponding to selection criteria")
    parser.add_argument("-pl","--printing_keywords_list",nargs='+',type=str,dest="printing_keywords_list",help="list of stat file keywords whose values are printed out for selected models")
    
    # thresholds only apply to selection keywords
    parser.add_argument("-alt","--aggregate_lower_thresholds",nargs='+',type=float,dest="aggregate_lower_thresholds",help="aggregate lower thresholds")
    parser.add_argument("-aut","--aggregate_upper_thresholds",nargs='+',type=float,dest="aggregate_upper_thresholds",help="aggregate upper thresholds")
    parser.add_argument("-mlt","--member_lower_thresholds",nargs='+',type=float,dest="member_lower_thresholds",help="member lower thresholds")
    parser.add_argument("-mut","--member_upper_thresholds",nargs='+',type=float,dest="member_upper_thresholds",help="member upper thresholds")

    parser.add_argument("-e","--extract",default=False,dest="extract",action='store_true',help="Type -e to extract all good scoring model RMFs from the trajectory files")
    result = parser.parse_args()
 
    return result
    
def select_good_scoring_models():
     
    # process input
    arg=parse_args()
    
    gsms=GoodScoringModelSelector.GoodScoringModelSelector(arg.run_dir,arg.run_prefix)
               
    gsms.get_good_scoring_models(selection_keywords_list=arg.selection_keywords_list,printing_keywords_list=arg.printing_keywords_list,
    aggregate_lower_thresholds=arg.aggregate_lower_thresholds,aggregate_upper_thresholds=arg.aggregate_upper_thresholds,
    member_lower_thresholds=arg.member_lower_thresholds,member_upper_thresholds=arg.member_upper_thresholds,extract=arg.extract)
        
        
if __name__ == "__main__" :
    select_good_scoring_models()
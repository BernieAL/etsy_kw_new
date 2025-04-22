"""

Functions for:
    
    file creation
        makes file based on reqeust from user
        file name will be request_id (and date maybe?)
    file writing in specified format
        scraper worker imports this function, writes to file

    structure of report dir will be
        report root/
            user_id/
                date/
                    date_job_id_report.csv
"""

import os,sys
from pathlib import Path
from common.logger import get_logger


#env var path to output dir - same place for all reports
ROOT_REPORT_OUTPUT_DIR = "path/to/report-output-dir"

#setup logging for this worker
logger = get_logger("file_write_worker")


class ReportPathBuilder:

    def __init__(self,root_path):
        self.root = Path(root_path)
        self.root.mkdir(exist_ok=True) #ensure report root exists
        self.user_id_dir = None
        self.date_dir = None
        
        self.user_id = None
        self.job_id = None
        self.date = None

        self.curr_output_filepath = None

    def make_user_subdir(self,user_id):

        """

        this function takes the user_id making the request
        and makes the dir for user_id in report root

        
        
        report dir structure::::
                report root/
                    user_id/
                        date/
                            date_job_id_report.csv

        
        """
        self.user_id = user_id
        self.user_id_dir = self.root / user_id
        self.user_id_dir.mkdir(exist_ok=True)
        logger.info(f"Created user_id_dir: {self.user_id_dir}")
        return self.user_id_dir
    
    def make_date_subdir(self,date):
        """

        this function will make the date subdir in user_id subdir

        need to check if subdir exists for user_id
        if not make it - do this by calling make_user_subdir

        report dir structure::::
                report root/
                    user_id/
                        date/
                            date_job_id_report.csv

        
        """

        if self.user_id_dir is None:
            raise ValueError("User subdir must be created before date subdir")
        
        self.date = date
        self.date_dir = self.user_id_dir / date
        self.date_dir.mkdir(exist_ok=True)
  
        logger.info(f"created date_dir: {self.date_dir}")
        return self.date_dir

    def make_report_file(self,job_id):
        """
        create empty file, return filename back to scraper worker
        
        """
        self.job_id = job_id
     
        filename = f"{self.user_id}_{self.date_id}_{self.job_id}.csv"
        filepath = Path(self.root,self.user_id_dir,self.date_dir,filename)
        self.curr_output_filepath = filepath
        
        with open(filepath,'w') as f:
            pass

    def write_file_formatted(self,data):

        with open(self.curr_output_filepath,'w') as file:


            """
            format to write to file
                single row for each url
                tags and related searches will be in the format of 
                [";"] so we can put many in a single row for a single url
                this is to avoid multiple rows for a single url


            url, tags[";"], related searches[;]
            etsy/123,["kitchen,rustic,ceramic"],["home decor;small apartment"],
            etsy/124,["bedroom,rustic,green"],["home decor;open space"],
            """
            
                


    
def make_output_dir(ROOT_REPORT_OUTPUT_DIR):

    """
    Makes output dir if it doesn't exist already.
    """
    root_output_dir_path = Path(ROOT_REPORT_OUTPUT_DIR)
    
    if not root_output_dir_path.is_dir():
        root_output_dir_path.mkdir(exist_ok=True)
        logger.info(f"Created root_report_output_dir at {root_output_dir_path}")
    else:
        logger.info(f"EXISTS: root_report_output_dir at {root_output_dir_path}")

#!/usr/bin/python3.8
# installed from https://pypi.org/project/watchdog/

## Filepaths of scripts and directories
TCR_render_script = "/home/ionadmin/ngs_variant_annotation/variantAnnotation/scripts/TCR_Rmd_render_script.R"
NGS_annotation_R = "/home/ionadmin/ngs_variant_annotation/variantAnnotation/scripts/NGSannotation_pipeline.R"
bimi_check_R = "/home/ionadmin/ngs_variant_annotation/variantAnnotation/scripts/bimiCheck.R"
Patiendata_filepath = "/mnt/NGS_Diagnostik/Patientendaten/"



import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
import subprocess
import re
import os

### Patterns to check for
if __name__ == "__main__":
    patterns = ["*.tsv","*.clone_summary.csv"]
    ignore_patterns = ["*annotated*","Fusion.tsv", "Cnv.tsv", "Snv.tsv", "*variant_details.tsv", "Summary.tsv","summary.tsv"]
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)


#### Functions to run on change files
def on_created(event):
  print(f"File added {event.src_path}!")
  filepath = event.src_path

  ## Check if absolute filepath is tsv file
  filetest_std = re.search(".tsv$", filepath)


  ## Check if absolute filepath is clone summary file
  filetest_TCR = re.search(".clone_summary.csv$", filepath)

  ## Dirpath
  dirpath = os.path.dirname(filepath)

  ## TCR pipeline
  if(filetest_TCR != None):
      dirpath = os.path.dirname(filepath)
      subprocess.call(["/usr/bin/Rscript",
                       "--vanilla",
                       TCR_render_script,
                       "--dir",
                       dirpath,
                       "--file",
                       filepath])


  ## Standard file pipeline
  elif(filetest_std != None):
      subprocess.call(["/usr/bin/Rscript",
      "--vanilla", NGS_annotation_R,
      "--file",
      event.src_path])

def on_deleted(event):
  print(f"File deleted {event.src_path}!")

def on_modified(event):
    '''
    '''
    print(f"File modified {event.src_path}")


def on_moved(event):
  print(f"File moved from {event.src_path} to {event.dest_path}")


## how to handle change events

my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

### exception because of folder permissions (taken from https://github.com/spyder-ide/spyder/issues/12636)


## Observer -- monitors for file changes
path = Patiendata_filepath
go_recursively = True
my_observer = PollingObserver()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)


## Observer -- start and sleep for 10sec
my_observer.start()
try:
    while True:
        time.sleep(5)
        #print("Checking for new input files.")
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()

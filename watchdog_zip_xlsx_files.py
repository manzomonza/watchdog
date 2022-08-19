#!/usr/bin/python3.8
# installed from https://pypi.org/project/watchdog/

## Filepaths of scripts and directories
Patiendata_filepath = "/mnt/NGS_Diagnostik/Patientendaten/"
bimi_check_R = "/home/ionadmin/ngs_variant_annotation/variantAnnotation/scripts/bimiCheck.R"



import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
import subprocess
import re
import os
import zipfile

### Patterns to check for
if __name__ == "__main__":
    patterns = ["*combined*.xlsx", "*.zip"]
    ignore_patterns = ["donotuse"]
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns,ignore_patterns, ignore_directories, case_sensitive)


def unzipFile(zipfilepath):
    print('Trying to unpack')
    '''
    Normally 'zipfile.is_zipfile()' should already check if current file
    is zip. However, .xlsx are also being unzipped. Therefore, simple, but error
    prone, file ending regex is used to only select files ending in .zip to be
    checked by zipfile.is_zipfile().
    '''
    dirpath = os.path.dirname(zipfilepath)
    zip_ref=zipfile.ZipFile(zipfilepath, 'r')
    for file in zip_ref.namelist():
        if file.startswith('QC/') | file.startswith('CNV_VCIB/'):
            zip_ref.extract(file, dirpath)
    zip_ref.close()



#### Functions to run on change files
def on_created(event):
  print(f"File added {event.src_path}!")
  filepath = event.src_path
  dirpath = os.path.dirname(filepath)
  ## zip file pipeline
  filetest = re.search(".zip$", filepath)
  tcr_test = re.search('TCR', filepath)

  if(filetest != None):
      if(zipfile.is_zipfile(filepath)):
          if(tcr_test != None):
              print('tcr')
          else:
              unzipFile(filepath)


def on_deleted(event):
  print(f"File deleted {event.src_path}!")

def on_modified(event):
    '''
    Specifically checks changes on 'combined.xlsx', as this represent the manual
    interface to the functionality of the watchdog
    '''
    print(f"File modified {event.src_path}")
    filepath = event.src_path
    filetest = re.search(".xlsx$", filepath)
    if(filetest != None):
      subprocess.call(["/usr/bin/Rscript",
      "--vanilla", bimi_check_R,
      "--file",
      filepath])
      ## Git autocommit
      subprocess.call(['/usr/bin/sh', '/home/ionadmin/ngs_variant_annotation/variantAnnotation/NGS_mutation_list/autocommit.sh'])

def on_moved(event):
  print(f"File moved from {event.src_path} to {event.dest_path}")


## how to handle change events

my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved


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

#/usr/bin/R



## BIMI CHECK
## This script checks combined.xlsx  for differing BIMI Variants in 'Annotation' sheet and overwrites BIMI variant entry or adds novel BIMI Variant
## Script executing will be triggered by watchdog. Watchdog will run command upon noticed changes to combined.xlsx file
suppressPackageStartupMessages({
  
  library(tidyverse)
  library(parallel)
  library(janitor)
  library(data.table)
  library(readxl)
})

################################################# OPTPARSE ################################################# 
library(optparse)

option_list = list(
  make_option(c("-f", "--file"), type="character", default=NULL,
              help="dataset file name", metavar="character"))

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser)

print(opt$file)



############################################################ BIMI CHECK FUNCTION ############################################################ 
## Function to check for BIMI variant entries
## Short version just checks if BIMI of IR mutation table is not NA and is not already present in BIMI table
## Then returns entries to be added to BIMI table
bimiCheck_short <- function(singlerowxlsx, bimi_table){
  # bimi_table = bimi_table %>% 
  #   dplyr::select(-rowid) %>% 
  #   rowid_to_column()
  ## checks if BIMI variant is not NA
  if(!is.na(singlerowxlsx$BIMI_variant) & singlerowxlsx$BIMI_variant != ""){
    if(!singlerowxlsx$BIMI_variant %in% bimi_table$BIMI_variant){
      singlerowxlsx$Kommentar = "watchdog fetch"
      singlerowxlsx$entry_date = Sys.time()
      novelbimientry <- singlerowxlsx %>% 
        dplyr::select(all_of(bimiVariantcols))
      return(novelbimientry)
    }
  }
}



## READ in BIMI table
# Local MAC machine
# bimi_table <- read_tsv('/Volumes/GoogleDrive/.shortcut-targets-by-id/1yuFiN1dlcUgo1_ELdNVXegTfB61oDv8G/Patientendaten/NGS_mutation_list_v2/BIMI_Variant_table.tsv')

# IntelNUC
bimi_table <- readr::read_tsv("/home/ionadmin/ngs_variant_annotation/variantAnnotation/NGS_mutation_list/BIMI_Variant_table.tsv")

## generate vector of required columns 
bimiVariantcols <- colnames(bimi_table)
print(bimiVariantcols)


# #bimiCheck <- function(singlerowxlsx, bimi_table){
#   # bimi_table = bimi_table %>% 
#   #   dplyr::select(-rowid) %>% 
#   #   rowid_to_column()
#   ## checks if BIMI variant is not NA
#   if(!is.na(singlerowxlsx$BIMI_variant) & singlerowxlsx$BIMI_variant != ""){
#     bimi_table = bimi_table %>% 
#       tidyr::unite(col = 'unique_mutation', genes, amino_acid_change, remove = FALSE)
#     singlerowxlsx = singlerowxlsx %>% 
#       tidyr::unite(col = 'unique_mutation', genes, amino_acid_change, remove = FALSE)
#     
#     ## pull BIMI variant matching the same 'unique_mutation' entry of the annotated mutation table
#     bimi_table_BIMI <- bimi_table %>% 
#       dplyr::filter(unique_mutation %in% singlerowxlsx$unique_mutation) %>% pull(BIMI_variant)
#     
#     if(is.null(bimi_table_BIMI)){
#       singlerowxlsx$Kommentar = "watchdog fetch"
#       singlerowxlsx$entry_date = Sys.time()
#       novelbimientry <- singlerowxlsx %>% 
#         dplyr::select(all_of(bimiVariantcols))
#       return(novelbimientry)
#       
#     }else if(!singlerowxlsx$BIMI_variant %in% bimi_table_BIMI){
#       singlerowxlsx$Kommentar = "watchdog fetch"
#       singlerowxlsx$entry_date = Sys.time()
#       novelbimientry <- singlerowxlsx %>% 
#         dplyr::select(all_of(bimiVariantcols))
#       return(novelbimientry)
#     }
#   }
# }





# combined_files <- list.files(path = "/Volumes/GoogleDrive/.shortcut-targets-by-id/1yuFiN1dlcUgo1_ELdNVXegTfB61oDv8G/Patientendaten/2021/",
#            pattern = ".*combined.xlsx",
#            recursive = TRUE,
#            full.names = TRUE)
# 

# 
# 
# !exf$BIMI_variant[13] %in% bimi_table$BIMI_variant
# ######################## 
# 
# exf$BIMI_variant
#combined_files <- grep("~", combined_files, invert = TRUE, value = TRUE)


## FOR CHECKS ON MAC
# for (i in seq_along(combined_files)){
#   exf <- readxl::read_xlsx(combined_files[i],
#                            sheet = "Annotation") %>%
#     dplyr::select(-to_include_in_NGS_database, -contains('rowid')) %>%
#     rowid_to_column()
#   
#   new_bimi_entries <- bind_rows(lapply(exf$rowid, function(x) bimiCheck_short(exf[x,], bimi_table = bimi_table)))
#   
#   if(nrow(new_bimi_entries) >0){
#     bind_rows(bimi_table, new_bimi_entries) 
#   }
# }

exf <- readxl::read_xlsx(opt$file,
                         sheet = "Annotation") %>%
  dplyr::select(-contains("to_include_in_NGS_database"), -contains('rowid')) %>%
  rowid_to_column()

new_bimi_entries <- bind_rows(lapply(exf$rowid, function(x) bimiCheck_short(exf[x,], bimi_table = bimi_table)))

if(nrow(new_bimi_entries) >0){
  print("Adding new entries to BIMI table:")
  print(new_bimi_entries)
  write_tsv(new_bimi_entries, "/home/ionadmin/ngs_variant_annotation/variantAnnotation/NGS_mutation_list/BIMI_Variant_table.tsv",
            append = TRUE)
}



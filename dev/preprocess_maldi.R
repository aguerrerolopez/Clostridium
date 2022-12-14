###############################################################################
##
## MALDI-TOF Translator from Bruker to mzML
##
## Alejandro Guerrero-López
##
###############################################################################
args <- commandArgs(trailingOnly = TRUE)
###############################################################################
## Load libraries
## MALDIquant()
## MALDIquantForeign()
##
#install.packages(c("MALDIquant","MALDIquantForeign", "stringr"))
##############################################################################

library("MALDIquant")
library("MALDIquantForeign")
library("stringr")

###############################################################################
## Load data
###############################################################################
replicates <- args[1]
if (replicates>0) {id_pos<-5} else {id_pos<-4}

path_train <- paste(getwd(), "/data_to_predict", sep="")
path_export <- paste(getwd(), "/results/data_maldiquant", sep="")

spectra1 <- importBrukerFlex(path_train)

##### PREPROCESS

#Step 1: the measured intensity is transformed with a square-root method to stabilize the variance
spectraint <- transformIntensity(spectra1, method="sqrt")
# Step 2: smoothing using the Savitzky–Golay algorithm with half-window-size 5 is applied
spectrasmooth <- smoothIntensity(spectraint, method="SavitzkyGolay", halfWindowSize=5, polynomialOrder=3)
# Step 3: an estimate of the baseline 
spectrabase <- removeBaseline(spectrasmooth, method="TopHat")
# Step 4: replicates handling
if (replicates>0){
id_idx <- length(str_split(metaData(spectrabase[[1]])$file, "\\\\", simplify=TRUE))-id_pos
samples <- factor(sapply(sapply(spectrabase, function(x)metaData(x)$file), function(x)str_split(x, "\\\\", simplify=TRUE))[id_idx,])
avgSpectra <- averageMassSpectra(spectrabase, labels=samples, method="mean")
} else { avgSpectra <- spectrabase
}
# Step 5: alignment
#spectra_al <- alignSpectra(avgSpectra, halfWindowSize=20, SNR=2, tolerance=600e-6, warpingMethod="lowess")
# Step 6: the intensity is calibrated using the total ion current (TIC)
spectra_tic <- calibrateIntensity(avgSpectra, method="TIC")

###############################################################################
## Save data
###############################################################################
# path_save <- paste0(path, args[2])
# save(spectra1, file=args[2])
## Export
# exportMzMl(spectra_tic, path=path_save)
for (i in c(1:length(spectra_tic))){ 
    export(spectra_tic[i], file=paste(path_export, attributes(spectra_tic[i]), sep=""), type="csv", force=TRUE)
    }

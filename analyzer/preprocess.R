###############################################################################
# MALDI-TOF Translator from Bruker to mzML
#
# Authored by:
# - Alejandro Guerrero-López (https://github.com/aguerrerolopez)
#
# Adapted by:
# - José Miguel Moreno (https://github.com/josemmo)
###############################################################################

# Load dependencies
suppressMessages(library('MALDIquant'))
suppressMessages(library('MALDIquantForeign'))
library('stringr')

# Get path to sample directory
args <- commandArgs(trailingOnly=TRUE)
sample_path <- args[1]

# Load sample
spectra <- importBrukerFlex(sample_path)

# Step 1: the measured intensity is transformed with a square-root method to stabilize the variance
spectraint <- transformIntensity(spectra, method='sqrt')

# Step 2: smoothing using the Savitzky–Golay algorithm with half-window-size 5 is applied
spectrasmooth <- smoothIntensity(spectraint, method='SavitzkyGolay', halfWindowSize=5, polynomialOrder=3)

# Step 3: an estimate of the baseline
spectrabase <- removeBaseline(spectrasmooth, method='TopHat')

# Step 4: the intensity is calibrated using the total ion current (TIC)
spectra_tic <- calibrateIntensity(spectrabase, method='TIC')

# Output CSV outputs for every sample
for (i in c(1:length(spectra_tic))) {
    digest = metaData(spectra_tic[[i]])$sampleName
    cat('[', digest, ']\n', sep='')
    write.table(as.matrix(spectra_tic[[i]]), sep=',', row.names=FALSE, col.names=FALSE)
}

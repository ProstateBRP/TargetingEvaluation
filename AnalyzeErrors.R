path = "/Users/junichi/Projects/BRP/BRPRobotCases/Scene"
#dataFile = "result-2015-09-28-23-34-36.csv"
#dataFile = "result-2015-10-28-09-09-31.csv"
#dataFile = "result-2016-09-28-11-49-46.csv"
dataFile = "Combined-result-2016-11-28-preliminary.csv"
data = read.csv(sprintf("%s/%s", path, dataFile))

# Process

n <- nrow(data)

## Check first and last attempts
first <- c(TRUE)
last <- c(FALSE)

for (i in 2:n) {
    # First attempt
    if ((data$Case[i] != data$Case[i-1]) || (data$Target[i] != data$Target[i-1])) {
        first <- c(first, TRUE)
    } else {
        first <- c(first, FALSE)
    }
    # Last attempt
    if ((i >= n) || (data$Target[i] != data$Target[i+1])) {
        last <- c(last, TRUE)
    } else {
        last <- c(last, FALSE)
    }
}

data$First <- first
data$Last <- last
data$Sampled <- (data$Core != -1)

## Generate case/target summary
caseNumTargets <- c()
targetNumAttempts <-c()
targetNumCores <-c()
numAttempts <- 0
numTargets <- 0
numCores <- 0
for (i in 1:n) {
    numAttempts <- numAttempts + 1
    if (data$Core[i] != -1) {
        numCores <- numCores + 1
    }
    if (i == n || (data$Case[i] != data$Case[i+1])) {
        numTargets <- numTargets + 1
        targetNumAttempts <- c(targetNumAttempts, numAttempts)
        targetNumCores <- c(targetNumCores, numCores)
        caseNumTargets <- c(caseNumTargets, numTargets)
        numTargets <- 0
        numAttempts <- 0
        numCores <- 0
    } else if (data$Target[i] != data$Target[i+1]) {
        numTargets <- numTargets + 1
        targetNumAttempts <- c(targetNumAttempts, numAttempts)
        targetNumCores <- c(targetNumCores, numCores)
        numAttempts <- 0
        numCores <- 0
    }
}


# Calculate estimated error angle
bevelAnglePrevious <- 0.0
estimatedAngles <- c()
for (i in 1:n) {
    if (data$First[i] == TRUE) {
        estimatedAngles <- c(estimatedAngles, 0.0)
    } else {
        if (bevelAnglePrevious >= 0.0 && data$BevelAngle[i] >= 0.0) {
            delta <- data$BevelAngle[i] - bevelAnglePrevious
            if (delta == 0.0){
                estimatedAngles <- c(estimatedAngles, -1.0)
            } else if (delta > 0.0) {
                est <- bevelAnglePrevious + 180.0 - (180.0 - delta) / 2.0
                if (est < 0.0) {
                    est <- est + 360.0
                } else if (est > 360.0) {
                    est <- est - 360.0
                }
                estimatedAngles <- c(estimatedAngles, est)
            } else {
                delta <- -delta
                est <- bevelAnglePrevious - (180.0 - (180.0 - delta) / 2.0)
                if (est < 0.0) {
                    est <- est + 360.0
                } else if (est > 360.0) {
                    est <- est - 360.0
                }
                estimatedAngles <- c(estimatedAngles, est)
            }
        } else {
            estimatedAngles <- c(estimatedAngles, -1)
        }
    }
    bevelAnglePrevious <- data$BevelAngle[i]
}

data$EstimatedErrorAngle <- estimatedAngles

## Summary
print(sprintf("Number of Targets / Case       : %.3f", mean(caseNumTargets)))
print(sprintf("Number of Cores / Targets      : %.3f", mean(targetNumCores)))
print(sprintf("Number of Attempts / Core      : %.3f", sum(targetNumAttempts)/sum(targetNumCores)))

print(sprintf("Targeting Error (all attempts) : %.3f +/- %.3f (mm)", mean(data$TgtErr), sd(data$TgtErr)))
print(sprintf("Targeting Error (1st attempts) : %.3f +/- %.3f (mm)", mean(data$TgtErr[data$First]), sd(data$TgtErr[data$First])))
#print(sprintf("Targeting Error (last attempts): %.3f +/- %.3f (mm)", mean(data$TgtErr[data$Last]), sd(data$TgtErr[data$Last])))
print(sprintf("Targeting Error (sampled)      : %.3f +/- %.3f (mm)", mean(data$TgtErr[data$Sampled]), sd(data$TgtErr[data$Sampled])))
print(sprintf("Biopsy Error (all attempts)    : %.3f +/- %.3f (mm)", mean(data$BxErr), sd(data$BxErr)))
print(sprintf("Biopsy Error (1st attempts)    : %.3f +/- %.3f (mm)", mean(data$BxErr[data$First]), sd(data$BxErr[data$First])))
#print(sprintf("Biopsy Error (last attempts)   : %.3f +/- %.3f (mm)", mean(data$BxErr[data$Last]), sd(data$BxErr[data$Last])))
print(sprintf("Biopsy Error (sampled)         : %.3f +/- %.3f (mm)", mean(data$BxErr[data$Sampled]), sd(data$BxErr[data$Sampled])))


print(sprintf("RMS Targeting Error (all attempts) : %.3f (mm)", sqrt(mean(data$TgtErr^2))))
print(sprintf("RMS Targeting Error (1st attempts) : %.3f (mm)", sqrt(mean(data$TgtErr[data$First]^2))))
print(sprintf("RMS Targeting Error (sampled)      : %.3f (mm)", sqrt(mean(data$TgtErr[data$Sampled]^2))))
print(sprintf("RMS Biopsy Error (all attempts)    : %.3f (mm)", sqrt(mean(data$BxErr^2))))
print(sprintf("RMS Biopsy Error (1st attempts)    : %.3f (mm)", sqrt(mean(data$BxErr[data$First]^2))))
print(sprintf("RMS Biopsy Error (sampled)         : %.3f (mm)", sqrt(mean(data$BxErr[data$Sampled]^2))))


##
## Distance vs Targeting Error
##
#R = cor( data$DepthEnd, data$TgtErr )
#pdf(sprintf("%s/Result-Distance-TgtError.pdf", path))
#reg1 <- lm(data$DepthEnd~data$TgtErr)
#plot(data$DepthEnd, data$TgtErr, main=sprintf("Needle Insertion Depth vs Targeting Error (r=%f)", R), xlab="Insertion Depth (mm)", ylab="Targeting Error (mm)")
#abline(reg1)
#dev.off()


##
## Targeting Errors in RL
##
t = t.test(data$TgtErrR[data$SegmentLR=='R'], data$TgtErrR[data$SegmentLR=='L'])
pdf(sprintf("%s/Result-SegmentLR-TgtErrorR.pdf", path))
plot(data$SegmentLR, data$TgtErrR, main=sprintf("Target Region vs Targeting Error (R-L) (p=%.8f)", t$p.value), xlab="Target Region", ylab="R-L Targeting Error (mm)")
dev.off()

##
## Targeting Errors in AP
##
data$SegmentAP <- factor(data$SegmentAP)
levels(data$SegmentAP)[levels(data$SegmentAP)==1] <- 'A'
levels(data$SegmentAP)[levels(data$SegmentAP)==0] <- 'P'
t = t.test(data$TgtErrR[data$SegmentAP=='A'], data$TgtErrR[data$SegmentAP=='P'])
pdf(sprintf("%s/Result-SegmentAP-TgtErrorA.pdf", path))
plot(data$SegmentAP, data$TgtErrA, main=sprintf("Target Region vs Targeting Error (A-P) (p=%f)", t$p.value), xlab="Target Region", ylab="A-P Targeting Error (mm)")
dev.off()

##
## Targeting Errors in AMB
##
t.am = t.test(data$TgtErr[data$SegmentAB=='A'], data$TgtErr[data$SegmentAB=='M'])
t.mb = t.test(data$TgtErr[data$SegmentAB=='M'], data$TgtErr[data$SegmentAB=='B'])
t.ab = t.test(data$TgtErr[data$SegmentAB=='A'], data$TgtErr[data$SegmentAB=='B'])
pdf(sprintf("%s/Result-SegmentAB-TgtError.pdf", path))
plot(data$SegmentAB, data$TgtErr, main="Target Region vs Targeting Error (Apex/Base/Mid)", xlab=sprintf( "Target Region (A vs M: p=%f; M vs B: p=%f; A vs B: p=%f)", t.am$p.value, t.mb$p.value, t.ab$p.value), ylab="Targeting Error (mm)")
dev.off()



##
## Targeting Errors in RL
##

wtest <- wilcox.test(data$TgtErr[data$SegmentLR=='R'], data$TgtErr[data$SegmentLR=='L'])
print(sprintf("RMS Errors (Left/Right): L = %f mm; R = %f mm (p = %f)", sqrt(mean(data$TgtErr[data$SegmentLR=='L']^2)), sqrt(mean(data$TgtErr[data$SegmentLR=='R']^2)), wtest$p.value))

##
## Targeting Errors in AP
##

wtest <- wilcox.test(data$TgtErr[data$SegmentAP=='A'], data$TgtErr[data$SegmentAP=='P'])
print(sprintf("RMS Errors (Anterior/Posterior): A = %f mm; P = %f mm (p = %f)", sqrt(mean(data$TgtErr[data$SegmentAP=='A']^2)), sqrt(mean(data$TgtErr[data$SegmentAP=='P']^2)), wtest$p.value))

##
## Targeting Errors in AMB
##
wtest.am <- wilcox.test(data$TgtErr[data$SegmentAB=='A'], data$TgtErr[data$SegmentAB=='M'])
wtest.mb <- wilcox.test(data$TgtErr[data$SegmentAB=='M'], data$TgtErr[data$SegmentAB=='B'])
wtest.ab <- wilcox.test(data$TgtErr[data$SegmentAB=='A'], data$TgtErr[data$SegmentAB=='B'])
print(sprintf("RMS Errors (Apex/Mid/Base: A = %f mm; M = %f mm; B = %f mm (p(AM) = %f; p(MB) = %f; p(AB) = %f)", sqrt(mean(data$TgtErr[data$SegmentAB=='A']^2)), sqrt(mean(data$TgtErr[data$SegmentAB=='M']^2)), sqrt(mean(data$TgtErr[data$SegmentAB=='B']^2)), wtest.am$p.value, wtest.mb$p.value, wtest.ab$p.value))

#
# Attempts vs Location
                                        #
averageAttempts <- targetNumAttempts / targetNumCores
targetSegmentLR <- data$SegmentLR[data$First==TRUE]
targetSegmentAP <- data$SegmentAP[data$First==TRUE]
targetSegmentAB <- data$SegmentAB[data$First==TRUE]

print(wilcox.test(averageAttempts[targetSegmentLR=='R'], averageAttempts[targetSegmentLR=='L']))
print(wilcox.test(averageAttempts[targetSegmentAP=='A'], averageAttempts[targetSegmentAP=='P']))
print(wilcox.test(averageAttempts[targetSegmentAB=='A'], averageAttempts[targetSegmentAB=='B']))

print(sprintf("Average # of attempts (Left/Right): %f vs %f", mean(averageAttempts[targetSegmentLR=='R']), mean(averageAttempts[targetSegmentLR=='L'])))
print(sprintf("Average # of attempts (Anterior/Posterior): %f vs %f", mean(averageAttempts[targetSegmentAP=='A']), mean(averageAttempts[targetSegmentAP=='P'])))
print(sprintf("Average # of attempts (Apex/Mid/Base): %f vs %f vs %f", mean(averageAttempts[targetSegmentAB=='A']), mean(averageAttempts[targetSegmentAB=='M']), mean(averageAttempts[targetSegmentAB=='B'])))


##
## Bevel tip orientation (clockwise angle from 12 O'clock) vs Targeting Error orientation (orientation of the offset vector from the robot target)
##
maskForAngle <- (data$BevelAngle>=0)
R = cor( data$BevelAngle[maskForAngle], data$TgtErrAngle[maskForAngle] )
pdf(sprintf("%s/Result-BevelTip-TgtError.pdf", path))
reg1 <- lm(data$BevelAngle[maskForAngle]~data$TgtErrAngle[maskForAngle])
plot(data$BevelAngle[maskForAngle], data$TgtErrAngle[maskForAngle], main=sprintf("Bevel Tip Orientation vs Target Error Orientation (R=%f)", R), xlab="Tip Orientation (deg)", ylab="Targeting Error Orientation (deg)")
abline(reg1)
dev.off()


##
## Bevel tip orientation (clockwise angle from 12 O'clock) vs Biopsy Error orientation (orientation of the offset vector from the biopsy target)
##
pdf(sprintf("%s/BevelTip-BipsyError.pdf", path))
R = cor( data$BevelAngle[maskForAngle], data$BxErrAngle[maskForAngle] )
plot(data$BevelAngle[maskForAngle], data$BxErrAngle[maskForAngle], main=sprintf("Bevel Tip Orientation vs Biopsy Error Orientation (R=%f)", R), xlab="Tip Orientation (deg)", ylab="Biopsy Error Orientation (deg)")
dev.off()
cor.test( data$BevelAngle[maskForAngle], data$DeltaTgtErrAngle[maskForAngle])

pdf(sprintf("%s/test3.pdf", path))
plot(data$BevelAngle[maskForAngle], data$DeltaBxErrAngle[maskForAngle], main="Bevel Tip Orientation vs Error Orientation (From the 1st Attempt)", xlab="Tip Orientation (deg)", ylab="Error Orientation (deg)")
dev.off()
cor.test(data$BevelAngle[maskForAngle], data$DeltaBxErrAngle[maskForAngle])

pdf(sprintf("%s/test4.pdf", path))
plot(data$EstimatedErrorAngle[maskForAngle & (data$EstimatedErrorAngle>=0.0)], data$DeltaTgtErrAngle[maskForAngle & (data$EstimatedErrorAngle>=0.0)], main="Bevel Tip Orientation vs Estimated Error Orientation (From the 1st Attempt)", xlab="Tip Orientation (deg)", ylab="Error Orientation (deg)")
dev.off()

#dev.new()
#plot(data$SegmentLR, data$TgtErrR, main="Target Region (R/L) vs R-L Targeting Error", xlab="Target Region", ylab="R-L Targeting Error (mm)")
#dev.new()
#plot(data$SegmentLR, data$BxErrR, main="Target Region (R/L) vs R-L Biopsy Error", xlab="Target Region", ylab="R-L Biopsy Error (mm)")
#
#dev.new()
#plot(data$SegmentAB, data$TgtErr, main="Target Region (Apex/Base/Mid) vs Targeting Error", xlab="Target Region", ylab="Targeting Error (mm)")
#dev.new()
#plot(data$SegmentAB, data$BxErr, main="Target Region (Apex/Base/Mid) vs Targeting Error", xlab="Target Region", ylab="Targeting Error (mm)")
#
#dev.new()
#plot(data$SegmentZone, data$TgtErr, main="Target Region (PZ/CG/TZ) vs Targeting Error", xlab="Target Region (PZ/CG/TZ)", ylab="Targeting Error (mm)")


## Shift of the targets
tgtDispRMS <- sqrt(mean(data$TgtDispR^2+data$TgtDispA^2+data$TgtDispS^2))
print(sprintf('RMS Target Displacement: %f mm', tgtDispRMS))
print(sprintf('Target Displacement Right-Left: %f +/- %f mm', mean(data$TgtDispR), sd(data$TgtDispR)))
print(sprintf('Target Displacement Anterior-Posterior: %f +/- %f mm', mean(data$TgtDispA), sd(data$TgtDispA)))
print(sprintf('Target Displacement Superior-Inferior: %f +/- %f mm', mean(data$TgtDispS), sd(data$TgtDispS)))

## Trajectory Analysis
#
# Objects -- see AnalyzeTrajectory.py
#  0, # Not defined -- Reserved
#  1, # Prostate, 2
#  2, # Pelvic Diaphragm, 3
#  3, # Bulbospongiosus m., 4
#  4, # Bulb of the Penus / Corpus Spongiosum, 16
#  5, # Ischiocavernosus m., 5
#  6, # Crus of the Penis / Corpus Cavernosum, 6
#  7, # Transverse Perineal m., 13
#  8, # Obturator internus m., 10
#  9, # Rectum, 8
#  10,# Pubic Arc

CompareImpact <- function(objName, lenData, angData) {
  # Difference in accuracy
  mask <- ((data$Finger == 0) & (data$VIBE == 1))
  tgtWith <- data$TgtErr[mask & lenData > 0.0]
  tgtWithout <- data$TgtErr[mask & lenData == 0.0]
  print(sprintf("%s (Non-Intersect vs Intersect) : %.3f +/- %.3f (mm) vs %.3f +/- %.3f (mm)", objName, mean(tgtWithout), sd(tgtWithout), mean(tgtWith), sd(tgtWith)))
}

PlotImpact <- function(objName, paramName, paramUnit, param, errorName, errorUnit, error, isIntersec) {
  # Correlation between intersecting length and error
  mask <- ((data$Finger == 0) & (data$VIBE == 1))
  pdf(sprintf("%s/Plot - %s vs %s -%s.pdf", path, paramName, errorName, objName))
  p <- param[mask & isIntersec]
  e <- error[mask & isIntersec]
  R <- cor(p, e)
  plot(p, e, main=sprintf("%s: %s vs %s (R=%f)", objName, paramName, errorName, R), xlab=sprintf("%s (%s)", paramName, paramUnit), ylab=sprintf("%s (%s)", errorName, errorUnit))
  dev.off()
}

# Bevel tip vs error direction
PlotImpact("Bevel Tip Angle", "Tip Direction", "deg", data$BevelAngle,  "Targeting Error Direction", "deg", data$TgtErrAngle, data$BevelAngle > 0)

CompareImpact("Intersection Prostate",               data$Len_1, data$EntAng_1)
CompareImpact("Intersection Pelvic Diaphragm",       data$Len_2, data$EntAng_2)
CompareImpact("Intersection Bulbospongiosus m.",     data$Len_3, data$EntAng_3)
CompareImpact("Intersection Bulb of the Pneus",      data$Len_4, data$EntAng_4)
CompareImpact("Intersection Ishiocavernosus m.",     data$Len_5, data$EntAng_5)
CompareImpact("Intersection Crus of the Penis",      data$Len_6, data$EntAng_6)
CompareImpact("Intersection Transverse Perineal m.", data$Len_7, data$EntAng_7)
CompareImpact("Intersection Obturator internus m.",  data$Len_8, data$EntAng_8)
CompareImpact("Intersection Rectum",                 data$Len_9, data$EntAng_9)
CompareImpact("Intersection Pubic Arc",              data$Len_10, data$EntAng_10)

PlotImpact("Prostate",               "Intersecting Length", "mm", data$Len_1, "Targeting Error", "mm", data$TgtErr, data$Len_1 > 0)
PlotImpact("Pelvic Diaphragm",       "Intersecting Length", "mm", data$Len_2, "Targeting Error", "mm", data$TgtErr, data$Len_2 > 0)
PlotImpact("Bulbospongiosus m.",     "Intersecting Length", "mm", data$Len_3, "Targeting Error", "mm", data$TgtErr, data$Len_3 > 0)
PlotImpact("Bulb of the Pneus",      "Intersecting Length", "mm", data$Len_4, "Targeting Error", "mm", data$TgtErr, data$Len_4 > 0)
PlotImpact("Ishiocavernosus m.",     "Intersecting Length", "mm", data$Len_5, "Targeting Error", "mm", data$TgtErr, data$Len_5 > 0)
PlotImpact("Crus of the Penis",      "Intersecting Length", "mm", data$Len_6, "Targeting Error", "mm", data$TgtErr, data$Len_6 > 0)
PlotImpact("Transverse Perineal m.", "Intersecting Length", "mm", data$Len_7, "Targeting Error", "mm", data$TgtErr, data$Len_7 > 0)
PlotImpact("Obturator internus m.",  "Intersecting Length", "mm", data$Len_8, "Targeting Error", "mm", data$TgtErr, data$Len_8 > 0)
PlotImpact("Rectum",                 "Intersecting Length", "mm", data$Len_9, "Targeting Error", "mm", data$TgtErr, data$Len_9 > 0)
# PlotImpact("Pubic Arc",              "Length", "mm", data$Len_10, "Targeting Error", "mm", data$TgtErr, data$Len_10 > 0)

# Re-calculate TgtErrAngle with a range [-pi, pi]
errDir <- 180 * atan2(-data$TgtErrR, data$TgtErrA) / pi
PlotImpact("Prostate",               "Entry Direction", "deg", data$EntDir_1,  "Targeting Error Direction", "deg", errDir, data$Len_1 > 0)
PlotImpact("Pelvic Diaphragm",       "Entry Direction", "deg", data$EntDir_2,  "Targeting Error Direction", "deg", errDir, data$Len_2 > 0)
PlotImpact("Bulbospongiosus m.",     "Entry Direction", "deg", data$EntDir_3,  "Targeting Error Direction", "deg", errDir, data$Len_3 > 0)
PlotImpact("Bulb of the Pneus",      "Entry Direction", "deg", data$EntDir_4,  "Targeting Error Direction", "deg", errDir, data$Len_4 > 0)
PlotImpact("Ishiocavernosus m.",     "Entry Direction", "deg", data$EntDir_5,  "Targeting Error Direction", "deg", errDir, data$Len_5 > 0)
PlotImpact("Crus of the Penis",      "Entry Direction", "deg", data$EntDir_6,  "Targeting Error Direction", "deg", errDir, data$Len_6 > 0)
PlotImpact("Transverse Perineal m.", "Entry Direction", "deg", data$EntDir_7,  "Targeting Error Direction", "deg", errDir, data$Len_7 > 0)
PlotImpact("Obturator internus m.",  "Entry Direction", "deg", data$EntDir_8,  "Targeting Error Direction", "deg", errDir, data$Len_8 > 0)
PlotImpact("Rectum",                 "Entry Direction", "deg", data$EntDir_9,  "Targeting Error Direction", "deg", errDir, data$Len_9 > 0)
# PlotImpact("Pubic Arc",              "Direction", "deg", data$EntDir_10, "Targeting Error Direction", "deg", errDir, data$Len_10 > 0)

PlotImpact("Prostate",               "Entry Angle", "deg", data$EntAng_1,  "Targeting Error", "mm", data$TgtErr, data$Len_1 > 0)
PlotImpact("Pelvic Diaphragm",       "Entry Angle", "deg", data$EntAng_2,  "Targeting Error", "mm", data$TgtErr, data$Len_2 > 0)
PlotImpact("Bulbospongiosus m.",     "Entry Angle", "deg", data$EntAng_3,  "Targeting Error", "mm", data$TgtErr, data$Len_3 > 0)
PlotImpact("Bulb of the Pneus",      "Entry Angle", "deg", data$EntAng_4,  "Targeting Error", "mm", data$TgtErr, data$Len_4 > 0)
PlotImpact("Ishiocavernosus m.",     "Entry Angle", "deg", data$EntAng_5,  "Targeting Error", "mm", data$TgtErr, data$Len_5 > 0)
PlotImpact("Crus of the Penis",      "Entry Angle", "deg", data$EntAng_6,  "Targeting Error", "mm", data$TgtErr, data$Len_6 > 0)
PlotImpact("Transverse Perineal m.", "Entry Angle", "deg", data$EntAng_7,  "Targeting Error", "mm", data$TgtErr, data$Len_7 > 0)
PlotImpact("Obturator internus m.",  "Entry Angle", "deg", data$EntAng_8,  "Targeting Error", "mm", data$TgtErr, data$Len_8 > 0)
PlotImpact("Rectum",                 "Entry Angle", "deg", data$EntAng_9,  "Targeting Error", "mm", data$TgtErr, data$Len_9 > 0)


# maskForTrajectory <- ((data$Finger == 0) & (data$VIBE == 1))
# print("=== Impact of Anatomical Structures ===")
# TgtErrWithPD = data$TgtErr[maskForTrajectory & data$Len_2>0.0]
# TgtErrWithoutPD = data$TgtErr[maskForTrajectory & data$Len_2==0.0]
# print(sprintf("Pelvic Diaphragm (Non-Intersect vs Intersect) : %.3f +/- %.3f (mm) vs %.3f +/- %.3f (mm)", mean(TgtErrWithoutPD), sd(TgtErrWithoutPD), mean(TgtErrWithPD), sd(TgtErrWithPD)))
#
# TgtErrWithBSM = data$TgtErr[maskForTrajectory & data$Len_4>0.0]
# TgtErrWithoutBSM = data$TgtErr[maskForTrajectory & data$Len_4==0.0]
# print(sprintf("Bulbospongiosus m. (Non-Intersect vs Intersect) : %.3f +/- %.3f (mm) vs %.3f +/- %.3f (mm)", mean(TgtErrWithoutBSM), sd(TgtErrWithoutBSM), mean(TgtErrWithBSM), sd(TgtErrWithBSM)))

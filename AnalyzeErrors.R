path = "/Users/junichi/Dropbox/Experiments/BRP/BRPRobotCases/Scene/"
#dataFile = "result-2015-09-28-23-34-36.csv"
dataFile = "result-2015-10-28-09-09-31.csv"
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
R = cor( data$DepthEnd, data$TgtErr )
pdf(sprintf("%s/Result-Distance-TgtError.pdf", path))
reg1 <- lm(data$DepthEnd~data$TgtErr)
plot(data$DepthEnd, data$TgtErr, main=sprintf("Needle Insertion Depth vs Targeting Error (r=%f)", R), xlab="Insertion Depth (mm)", ylab="Targeting Error (mm)")
abline(reg1)
dev.off()


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





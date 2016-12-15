path <- "/Users/junichi/Projects/BRP/BRPRobotCases/Scene"
dataFile <- "Combined-result-2016-12-06-preliminary.csv"
rawdata <- read.csv(sprintf("%s/%s", path, dataFile))

mask <- ((rawdata$Finger == 0) & (rawdata$VIBE == 1) & (rawdata$Len_1 > 0))

data <- rawdata[mask, ]


Concat <- function(data1, data2, name) {
    
    names(data1) <- c(name)
    names(data2) <- c(name)
    C <- rbind(data1, data2)
    rownames(C) <- NULL  # Fix irregular row number
    return (C)
    
}


ConcatRA <- function(data, prefix) {

    R <- data[c(sprintf("%sR", prefix))]
    A <- data[c(sprintf("%sA", prefix))]
    C <- Concat(R, A, prefix)
    return (C)
    
}

AngleToVector <- function(data, srcName, dstName) {
    
    angle <- data[c(srcName)] * pi / 180.0
    normR <- - sin(angle)
    normA <- cos(angle)
    norm <- Concat(normR, normA, "bevelNorm")

    return (norm)
}


## 1. Simple model based on the length
RunSimpleModel <- function(data) {

    subdata <- data[c("TgtErr", "Len_1", "Len_2", "Len_3", "Len_4", "Len_5", "Len_6", "Len_7", "Len_8", "Len_9")]
    plot(subdata, pch=16, col="blue", main="Matrix Scatterplot of Targeting Error and Length in Each Structure")
    
    set.seed(1)
    
    TgtErr.c = scale(subdata$TgtErr, center=TRUE, scale=FALSE)
    Len_1.c = scale(subdata$Len_1, center=TRUE, scale=FALSE)
    Len_2.c = scale(subdata$Len_2, center=TRUE, scale=FALSE)
    Len_3.c = scale(subdata$Len_3, center=TRUE, scale=FALSE)
    Len_4.c = scale(subdata$Len_4, center=TRUE, scale=FALSE)
    Len_5.c = scale(subdata$Len_5, center=TRUE, scale=FALSE)
    Len_6.c = scale(subdata$Len_6, center=TRUE, scale=FALSE)
    Len_7.c = scale(subdata$Len_7, center=TRUE, scale=FALSE)
    Len_8.c = scale(subdata$Len_8, center=TRUE, scale=FALSE)
    Len_9.c = scale(subdata$Len_9, center=TRUE, scale=FALSE)
    
    new.c.vars <- cbind(TgtErr.c,Len_1.c,Len_2.c,Len_3.c,Len_4.c,Len_5.c,Len_6.c,Len_7.c,Len_8.c,Len_9.c)
    subdata <- cbind(subdata, new.c.vars)
    names(subdata)[11:20] = c("TgtErr.c","Len_1.c","Len_2.c","Len_3.c","Len_4.c","Len_5.c","Len_6.c","Len_7.c","Len_8.c","Len_9.c")
    
    mod1 = lm(TgtErr.c ~ Len_1.c + Len_2.c + Len_3.c + Len_4.c + Len_5.c + Len_6.c + Len_7.c + Len_8.c + Len_9.c, data=subdata)

    print (summary(mod1))
    #return (subdata)
}

## 2. Bevel tip in the stiff structure
RunBevelTipModel <- function(data) {

    # bevelAngle <- data[c("BevelAngle")] * pi / 180.0
    # bevelNormR <- - sin(bevelAngle)
    # bevelNormA <- cos(bevelAngle)
    # bevelNorm <- Concat(bevelNormR, bevelNormA, "bevelNorm")

    bevelNorm <- AngleToVector(data, "BevelAngle", "bevelNorm")
    
    ConcatLen_1 <- Concat(data[c("Len_1")], data[c("Len_1")], "Len_1")
    ConcatLen_2 <- Concat(data[c("Len_2")], data[c("Len_2")], "Len_2")
    ConcatLen_3 <- Concat(data[c("Len_3")], data[c("Len_3")], "Len_3")
    ConcatLen_4 <- Concat(data[c("Len_4")], data[c("Len_4")], "Len_4")
    ConcatLen_5 <- Concat(data[c("Len_5")], data[c("Len_5")], "Len_5")
    ConcatLen_6 <- Concat(data[c("Len_6")], data[c("Len_6")], "Len_6")
    ConcatLen_7 <- Concat(data[c("Len_7")], data[c("Len_7")], "Len_7")
    ConcatLen_8 <- Concat(data[c("Len_8")], data[c("Len_8")], "Len_8")
    ConcatLen_9 <- Concat(data[c("Len_9")], data[c("Len_9")], "Len_9")
    
    # Len * bevelNorm
    lenBevelNorm_1 <- bevelNorm * ConcatLen_1 
    lenBevelNorm_2 <- bevelNorm * ConcatLen_2
    lenBevelNorm_3 <- bevelNorm * ConcatLen_3
    lenBevelNorm_4 <- bevelNorm * ConcatLen_4
    lenBevelNorm_5 <- bevelNorm * ConcatLen_5
    lenBevelNorm_6 <- bevelNorm * ConcatLen_6
    lenBevelNorm_7 <- bevelNorm * ConcatLen_7
    lenBevelNorm_8 <- bevelNorm * ConcatLen_8
    lenBevelNorm_9 <- bevelNorm * ConcatLen_9

    TgtErr <- ConcatRA(data, "TgtErr")

    new.vars <- cbind(TgtErr,lenBevelNorm_1,lenBevelNorm_2,lenBevelNorm_3,lenBevelNorm_4,lenBevelNorm_5,lenBevelNorm_6,lenBevelNorm_7,lenBevelNorm_8,lenBevelNorm_9)
    names(new.vars)[2:10] <- c("LenBevelNorm_1","LenBevelNorm_2","LenBevelNorm_3","LenBevelNorm_4","LenBevelNorm_5","LenBevelNorm_6","LenBevelNorm_7","LenBevelNorm_8","LenBevelNorm_9")

    plot(new.vars, pch=16, col="blue", main="Matrix Scatterplot of Targeting Error and Length in Each Structure")

    
    TgtErr.c = scale(TgtErr, center=TRUE, scale=FALSE)
    lenBevelNorm_1.c = scale(lenBevelNorm_1, center=TRUE, scale=FALSE)
    lenBevelNorm_2.c = scale(lenBevelNorm_2, center=TRUE, scale=FALSE)
    lenBevelNorm_3.c = scale(lenBevelNorm_3, center=TRUE, scale=FALSE)
    lenBevelNorm_4.c = scale(lenBevelNorm_4, center=TRUE, scale=FALSE)
    lenBevelNorm_5.c = scale(lenBevelNorm_5, center=TRUE, scale=FALSE)
    lenBevelNorm_6.c = scale(lenBevelNorm_6, center=TRUE, scale=FALSE)
    lenBevelNorm_7.c = scale(lenBevelNorm_7, center=TRUE, scale=FALSE)
    lenBevelNorm_8.c = scale(lenBevelNorm_8, center=TRUE, scale=FALSE)
    lenBevelNorm_9.c = scale(lenBevelNorm_9, center=TRUE, scale=FALSE)

    new.vars.c <- cbind(TgtErr.c,lenBevelNorm_1.c,lenBevelNorm_2.c,lenBevelNorm_3.c,lenBevelNorm_4.c,lenBevelNorm_5.c,lenBevelNorm_6.c,lenBevelNorm_7.c,lenBevelNorm_8.c,lenBevelNorm_9.c)

    new.vars <- cbind(new.vars, new.vars.c)
    names(new.vars)[11:20] <- c("TgtErr.c", "LenBevelNorm_1.c","LenBevelNorm_2.c","LenBevelNorm_3.c","LenBevelNorm_4.c","LenBevelNorm_5.c","LenBevelNorm_6.c","LenBevelNorm_7.c","LenBevelNorm_8.c","LenBevelNorm_9.c")


    set.seed(1)
    mod1 = lm(TgtErr.c ~ LenBevelNorm_1.c + LenBevelNorm_2.c + LenBevelNorm_3.c + LenBevelNorm_4.c + LenBevelNorm_5.c + LenBevelNorm_6.c + LenBevelNorm_7.c + LenBevelNorm_8.c + LenBevelNorm_9.c, data=new.vars)

    print(summary(mod1))

    #return (mod1)
}



## 2. Bevel tip in the stiff structure
RunInterfaceModel <- function(data) {
    
    ConcatTgtErr <- ConcatRA(data, "TgtErr")

    ConcatEntAng_1 <- Concat(data[c("EntAng_1")], data[c("EntAng_1")], "EntAng_1")
    ConcatEntAng_2 <- Concat(data[c("EntAng_2")], data[c("EntAng_2")], "EntAng_2")
    ConcatEntAng_3 <- Concat(data[c("EntAng_3")], data[c("EntAng_3")], "EntAng_3")
    ConcatEntAng_4 <- Concat(data[c("EntAng_4")], data[c("EntAng_4")], "EntAng_4")
    ConcatEntAng_5 <- Concat(data[c("EntAng_5")], data[c("EntAng_5")], "EntAng_5")
    ConcatEntAng_6 <- Concat(data[c("EntAng_6")], data[c("EntAng_6")], "EntAng_6")
    ConcatEntAng_7 <- Concat(data[c("EntAng_7")], data[c("EntAng_7")], "EntAng_7")
    ConcatEntAng_8 <- Concat(data[c("EntAng_8")], data[c("EntAng_8")], "EntAng_8")
    ConcatEntAng_9 <- Concat(data[c("EntAng_9")], data[c("EntAng_9")], "EntAng_9")

    ConcatBendForce_1 <- sin(2.0*ConcatEntAng_1)
    ConcatBendForce_2 <- sin(2.0*ConcatEntAng_2)
    ConcatBendForce_3 <- sin(2.0*ConcatEntAng_3)
    ConcatBendForce_4 <- sin(2.0*ConcatEntAng_4)
    ConcatBendForce_5 <- sin(2.0*ConcatEntAng_5)
    ConcatBendForce_6 <- sin(2.0*ConcatEntAng_6)
    ConcatBendForce_7 <- sin(2.0*ConcatEntAng_7)
    ConcatBendForce_8 <- sin(2.0*ConcatEntAng_8)
    ConcatBendForce_9 <- sin(2.0*ConcatEntAng_9)

    ConcatEntNorm_1 <- AngleToVector(data, "EntDir_1", "entNorm_1")
    ConcatEntNorm_2 <- AngleToVector(data, "EntDir_2", "entNorm_2")
    ConcatEntNorm_3 <- AngleToVector(data, "EntDir_3", "entNorm_3")
    ConcatEntNorm_4 <- AngleToVector(data, "EntDir_4", "entNorm_4")
    ConcatEntNorm_5 <- AngleToVector(data, "EntDir_5", "entNorm_5")
    ConcatEntNorm_6 <- AngleToVector(data, "EntDir_6", "entNorm_6")
    ConcatEntNorm_7 <- AngleToVector(data, "EntDir_7", "entNorm_7")
    ConcatEntNorm_8 <- AngleToVector(data, "EntDir_8", "entNorm_8")
    ConcatEntNorm_9 <- AngleToVector(data, "EntDir_9", "entNorm_9")

    ConcatBendForceVec_1 <- ConcatBendForce_1 * ConcatEntNorm_1
    ConcatBendForceVec_2 <- ConcatBendForce_2 * ConcatEntNorm_2
    ConcatBendForceVec_3 <- ConcatBendForce_3 * ConcatEntNorm_3
    ConcatBendForceVec_4 <- ConcatBendForce_4 * ConcatEntNorm_4
    ConcatBendForceVec_5 <- ConcatBendForce_5 * ConcatEntNorm_5
    ConcatBendForceVec_6 <- ConcatBendForce_6 * ConcatEntNorm_6
    ConcatBendForceVec_7 <- ConcatBendForce_7 * ConcatEntNorm_7
    ConcatBendForceVec_8 <- ConcatBendForce_8 * ConcatEntNorm_8
    ConcatBendForceVec_9 <- ConcatBendForce_9 * ConcatEntNorm_9

    new.vars <- cbind(ConcatTgtErr, ConcatBendForceVec_1, ConcatBendForceVec_2, ConcatBendForceVec_3, ConcatBendForceVec_4, ConcatBendForceVec_5, ConcatBendForceVec_6, ConcatBendForceVec_7, ConcatBendForceVec_8, ConcatBendForceVec_9)
    names(new.vars)[1:10] <- c("TgtErr", "BendForceVec_1","BendForceVec_2","BendForceVec_3","BendForceVec_4","BendForceVec_5","BendForceVec_6","BendForceVec_7","BendForceVec_8","BendForceVec_9")

    ConcatTgtErr.c = scale(ConcatTgtErr, center=TRUE, scale=FALSE)
    ConcatBendForceVec_1.c = scale(ConcatBendForceVec_1, center=TRUE, scale=FALSE)
    ConcatBendForceVec_2.c = scale(ConcatBendForceVec_2, center=TRUE, scale=FALSE)
    ConcatBendForceVec_3.c = scale(ConcatBendForceVec_3, center=TRUE, scale=FALSE)
    ConcatBendForceVec_4.c = scale(ConcatBendForceVec_4, center=TRUE, scale=FALSE)
    ConcatBendForceVec_5.c = scale(ConcatBendForceVec_5, center=TRUE, scale=FALSE)
    ConcatBendForceVec_6.c = scale(ConcatBendForceVec_6, center=TRUE, scale=FALSE)
    ConcatBendForceVec_7.c = scale(ConcatBendForceVec_7, center=TRUE, scale=FALSE)
    ConcatBendForceVec_8.c = scale(ConcatBendForceVec_8, center=TRUE, scale=FALSE)
    ConcatBendForceVec_9.c = scale(ConcatBendForceVec_9, center=TRUE, scale=FALSE)

    new.vars.c <- cbind(ConcatTgtErr.c, ConcatBendForceVec_1.c, ConcatBendForceVec_2.c, ConcatBendForceVec_3.c, ConcatBendForceVec_4.c, ConcatBendForceVec_5.c, ConcatBendForceVec_6.c, ConcatBendForceVec_7.c, ConcatBendForceVec_8.c, ConcatBendForceVec_9.c)

    new.vars <- cbind(new.vars, new.vars.c)
    names(new.vars)[11:20] <- c("TgtErr.c", "BendForceVec_1.c","BendForceVec_2.c","BendForceVec_3.c","BendForceVec_4.c","BendForceVec_5.c","BendForceVec_6.c","BendForceVec_7.c","BendForceVec_8.c","BendForceVec_9.c")

    plot(new.vars, pch=16, col="blue", main="Matrix Scatterplot of Targeting Error and Length in Each Structure")
    
    set.seed(1)
    
    mod1 = lm(TgtErr.c ~ BendForceVec_1.c + BendForceVec_2.c + BendForceVec_3.c + BendForceVec_4.c + BendForceVec_5.c + BendForceVec_6.c + BendForceVec_7.c + BendForceVec_8.c + BendForceVec_9.c, data=new.vars)
    #mod1 = lm(TgtErr.c ~ BendForceVec_1.c + BendForceVec_3.c + BendForceVec_4.c + BendForceVec_7.c + BendForceVec_8.c, data=new.vars)

    print(summary(mod1))

}

    

args <- commandArgs(trailingOnly=TRUE)
root <- args[1]
source(file.path(root,'sources/ania/src/utils/kaos/R/distr.pts.R'))
source(file.path(root,'sources/ania/src/utils/kaos/R/cgr.R'))
seqs <- readLines(file.path(root,'inputs/sequences.txt'))
fcgr <- matrix(0,nrow=length(seqs),ncol=256)
con <- file(file.path(root,'results/cgr_coordinates.csv'),'w')
writeLines('index,position,x,y',con)
for (i in seq_along(seqs)) {
 chars <- strsplit(seqs[i],split='')[[1]]
 z <- cgr(chars, seq.base='AMINO',res=16)
 stopifnot(sum(z$matrix)==length(chars))
 fcgr[i,] <- as.vector(z$matrix)
 for (j in seq_along(chars)) writeLines(sprintf('%d,%d,%.17g,%.17g',i-1,j-1,z$x[j],z$y[j]),con)
}
close(con)
write.table(fcgr,file.path(root,'results/fcgr_native.csv'),sep=',',row.names=FALSE,col.names=FALSE)
writeLines(capture.output(sessionInfo()),file.path(root,'results/r_session.txt'))

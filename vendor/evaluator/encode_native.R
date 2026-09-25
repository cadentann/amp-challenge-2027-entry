args <- commandArgs(trailingOnly=TRUE)
source_root <- args[1]
input_path <- args[2]
output_root <- args[3]
source(file.path(source_root,'src/utils/kaos/R/distr.pts.R'))
source(file.path(source_root,'src/utils/kaos/R/cgr.R'))
seqs <- readLines(input_path)
fcgr <- matrix(0,nrow=length(seqs),ncol=256)
con <- file(file.path(output_root,'cgr_coordinates.csv'),'w')
writeLines('index,position,x,y',con)
for (i in seq_along(seqs)) {
 chars <- strsplit(seqs[i],split='')[[1]]
 z <- cgr(chars, seq.base='AMINO',res=16)
 stopifnot(sum(z$matrix)==length(chars))
 fcgr[i,] <- as.vector(z$matrix)
 for (j in seq_along(chars)) writeLines(sprintf('%d,%d,%.17g,%.17g',i-1,j-1,z$x[j],z$y[j]),con)
}
close(con)
write.table(fcgr,file.path(output_root,'fcgr_native.csv'),sep=',',row.names=FALSE,col.names=FALSE)
writeLines(capture.output(sessionInfo()),file.path(output_root,'r_session.txt'))

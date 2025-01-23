if (!require("readr", quietly = TRUE))
    install.packages("readr", ask = FALSE)

if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager", ask = FALSE)
BiocManager::install(version = "3.19", ask = FALSE)

if (!require("karyoploteR", quietly = TRUE))
    BiocManager::install("karyoploteR", ask = FALSE)

args = commandArgs(trailingOnly = TRUE)

mendel_check = readr::read_csv2(paste0(args[1], "/plot_chr.csv"))

mendel_check$chr = gsub("chr23", "chrX", mendel_check$chr)
mendel_check$chr = gsub("chr24", "chrY", mendel_check$chr)
mendel_check$chr = gsub("chr26", "chrMT", mendel_check$chr)

mendel_check_bed = mendel_check |> 
regioneR::toGRanges(y = NA)

png(filename = paste0(args[1], "/idiogram.png"), 
    width = 800, 
    height = 600)
p1 = karyoploteR::plotKaryotype(genome="hg19",
                        plot.type = 1,
                        chromosomes = unique(mendel_check$chr)) |>
karyoploteR::kpPoints(mendel_check_bed,
                        data.panel = 1,
                        pch = 15,
                        y = 0.001,
                        cex = 0.5)
dev.off()
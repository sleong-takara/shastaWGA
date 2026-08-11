library(ineq)
TrialX=readRDS("C:/Users/leongs/OneDrive - Takara Bio USA, Inc/Xuan Li's files - PLC1705/20260312_Trial16_Arcwell_Titration_Repeat/Chip#1/WGA_0.8x_analysis/dna_report_all/CogentAP_DNA_CNV_analysis.rds")
gini_scores <- apply(TrialX@assays[["ginkgo_data"]]$counts, MARGIN=2, FUN=Gini)
TrialX_gini <- as.data.frame(gini_scores)
#write.csv(TrialX_gini, "C:/Users/leongs/OneDrive - Takara Bio USA, Inc/Xuan Li's files - PLC1705/20260312_Trial16_Arcwell_Titration_Repeat/Chip#1/WGA_0.8x_analysis/dna_report_all/gini.csv")


TrialX_gini <- data.frame(
  cell = colnames(TrialX@assays[["ginkgo_data"]]$counts),
  gini = as.numeric(gini_scores),
  stringsAsFactors = FALSE
)

TrialX_gini$sample <- sub("_.*", "", TrialX_gini$cell)

sample_medians <- aggregate(gini ~ sample, data = TrialX_gini, FUN = median)
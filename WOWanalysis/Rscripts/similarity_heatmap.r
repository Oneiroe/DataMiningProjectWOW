library(gplots)

similarity_heatmap <- function(input_path, output_base_path) {
  # Plot heatmap of a distance matrix as is
  m <- read.csv(input_path)
  
  # distance matrix
  # d <- as.dist(t(as.matrix(m)), diag = TRUE, upper = TRUE)
  d <- data.matrix(m)

  # symmetric matrix
  sym <- pmax(d, t(d), na.rm = TRUE)
  
  # to PNG
  output_file <-
    file.path(output_base_path,
              paste0(tools::file_path_sans_ext(basename(input_path)), "_heatmap.png"),
              fsep = '\\')
  png(
    filename = output_file,
    width = 20,
    units = "in",
    res = 300,
    height = 20
  )

  # heatmap
  heatmap(
    sym,
    Rowv = NA,
    Colv = NA,
    symm = TRUE,
    margins = c(12, 8)
  )

  dev.off()
  return()
}

# args = commandArgs(trailingOnly = TRUE)
# if (length(args) == 2) {
#   similarity_heatmap(args[1], args[2])
# }


input_path <- "D:\\Università\\Data Mining\\PROJECT\\DataMiningProjectWOW\\Results\\similarity\\sorted_matrix_unique_c10[general].csv"
output_base_path <- "D:\\Università\\Data Mining\\PROJECT\\DataMiningProjectWOW\\Results\\similarity\\graphs"
similarity_heatmap(input_path, output_base_path)

library(gplots)
library(plotly)


similarity_3d <- function(input_path, sub_dim) {
  # data import
  m <- read.csv(input_path, header = FALSE)
  
  # distance matrix
  d <- data.matrix(m)
  
  test <- pmax(d, 0, na.rm = T)
  colnames(test) <- NULL
  p = plot_ly(z = test[0:sub_dim, 0:sub_dim], type = "surface")
  return(p)
}

submatrix_dimension <- 500


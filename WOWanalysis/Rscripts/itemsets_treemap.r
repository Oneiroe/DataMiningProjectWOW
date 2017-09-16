library(treemap)
library(d3treeR)
library(data.tree)
library(tibble)

itemsets_treemap <- function(data_plot_path, output_base_path) {
  # data import
  data_plot <- read.csv(data_plot_path)
  
  # data transformation
  tdp <- as_tibble(data_plot)
  
  # number of rows
  thresholds_num <- dim(tdp)[1]
  for (threshold in seq(1, thresholds_num)) {
    # number of frequent_itemsets_X fields
    baskets_num <-
      length(tdp[grep("frequent_itemsets_", names(tdp))])
    
    # groups
    columns <-
      c("distinct_items", colnames(tdp[grepl("^frequent_items_", names(tdp))]))
    
    group = c("tot", rep("frequent", baskets_num))
    
    subgroup = c("distinct_items", paste0("frequent_items_", seq(1, baskets_num)))
    
    # values
    value = c()
    for (i in columns) {
      value <- c(value, as.numeric(tdp[threshold, i]))
    }
    for (i in range(1, length(value) - 1)) {
      value[i] <- value[i] - value[i + 1]
    }
    
    
    data = data.frame(group,
                      subgroup,
                      value)
    
    # OUTPUT
    output_file <-
      file.path(
        output_base_path,
        paste0(
          tools::file_path_sans_ext(basename(data_plot_path)),
          "_treemap[",
          as.character(data_plot[threshold, 'threshold']),
          "].png"
        ),
        fsep = '\\'
      )
    png(filename = output_file,
        width = 1920,
        height = 1080)
    
    t = treemap(
      data,
      index = c("group",
                "subgroup"),
      vSize = "value",
      type = "index",
      title = output_file,
      align.labels = list(c("center", "center"),
                          c("center", "bottom")),
      palette = "Set2"
    )
    
    dev.off()
    
    output_file <-
      file.path(
        output_base_path,
        paste0(
          tools::file_path_sans_ext(basename(data_plot_path)),
          "_treemap_interactive[",
          as.character(data_plot[threshold, 'threshold']),
          "].html"
        ),
        fsep = '\\'
      )
    interactive = d3tree2(t)
    htmlwidgets::saveWidget(interactive, output_file)
  }
  return()
}

args = commandArgs(trailingOnly = TRUE)
if (length(args) == 2) {
  itemsets_treemap(args[1], args[2])
}

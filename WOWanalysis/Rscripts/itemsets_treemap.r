library(treemap)
library(d3treeR)
library(data.tree)
library(tibble)

itemsets_treemap <- function(data_plot_path, output_base_path) {
  # data import
  data_plot <- read.csv(data_plot_path)
  
  # data transformation
  tdp <- as_tibble(data_plot)
  
  # groups
  columns = c(
    "distinct_items",
    "frequent_items_1",
    "frequent_items_2",
    "frequent_items_3",
    "frequent_items_4",
    "frequent_items_5",
    "frequent_items_6",
    "frequent_items_7",
    "frequent_items_8",
    "frequent_items_9",
    "frequent_items_10",
    "frequent_items_11",
    "frequent_items_12",
    "frequent_items_13",
    "frequent_items_14",
    "frequent_items_15",
    "frequent_items_16",
    "frequent_items_17",
    "frequent_items_18"
  )
  # group= c(
  #   "distinct_items",
  #   "distinct_items",
  #   "frequent_items_1",
  #   "frequent_items_2",
  #   "frequent_items_3",
  #   "frequent_items_4",
  #   "frequent_items_5",
  #   "frequent_items_6",
  #   "frequent_items_7",
  #   "frequent_items_8",
  #   "frequent_items_9",
  #   "frequent_items_10",
  #   "frequent_items_11",
  #   "frequent_items_12",
  #   "frequent_items_13",
  #   "frequent_items_14",
  #   "frequent_items_15",
  #   "frequent_items_16",
  #   "frequent_items_17"
  # )
  group = c("tot", rep("frequent", 18))
  s_group = rep("total", 19)
  s_group_1 = c(rep("total", 1), rep("#1", 18))
  s_group_2 = c(rep("total", 1), rep("#1", 1), rep("#2", 17))
  s_group_3 = c(rep("total", 1), rep("#1", 1), rep("#2", 1), rep("#3", 16))
  s_group_4 = c(rep("total", 1),
                rep("#1", 1),
                rep("#2", 1),
                rep("#3", 1),
                rep("#4", 15))
  s_group_5 = c(rep("total", 1),
                rep("#1", 1),
                rep("#2", 1),
                rep("#3", 1),
                rep("#4", 1),
                rep("#5", 14))
  s_group_6 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 13)
  )
  s_group_7 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 12)
  )
  s_group_8 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 11)
  )
  s_group_9 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 1),
    rep("#9", 10)
  )
  s_group_10 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 1),
    rep("#9", 1),
    rep("#10", 9)
  )
  s_group_11 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 1),
    rep("#9", 1),
    rep("#10", 1),
    rep("#11", 8)
  )
  s_group_12 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 1),
    rep("#9", 1),
    rep("#10", 1),
    rep("#11", 1),
    rep("#12", 7)
  )
  s_group_13 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 1),
    rep("#9", 1),
    rep("#10", 1),
    rep("#11", 1),
    rep("#12", 1),
    rep("#13", 6)
  )
  s_group_14 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 1),
    rep("#9", 1),
    rep("#10", 1),
    rep("#11", 1),
    rep("#12", 1),
    rep("#13", 1),
    rep("#14", 5)
  )
  s_group_15 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 1),
    rep("#9", 1),
    rep("#10", 1),
    rep("#11", 1),
    rep("#12", 1),
    rep("#13", 1),
    rep("#14", 1),
    rep("#15", 4)
  )
  s_group_16 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 1),
    rep("#9", 1),
    rep("#10", 1),
    rep("#11", 1),
    rep("#12", 1),
    rep("#13", 1),
    rep("#14", 1),
    rep("#15", 1),
    rep("#16", 3)
  )
  s_group_17 = c(
    rep("total", 1),
    rep("#1", 1),
    rep("#2", 1),
    rep("#3", 1),
    rep("#4", 1),
    rep("#5", 1),
    rep("#6", 1),
    rep("#7", 1),
    rep("#8", 1),
    rep("#9", 1),
    rep("#10", 1),
    rep("#11", 1),
    rep("#12", 1),
    rep("#13", 1),
    rep("#14", 1),
    rep("#15", 1),
    rep("#16", 1),
    rep("#17", 2)
  )
  
  subgroup = c(
    "distinct_items",
    "frequent_items_1",
    "frequent_items_2",
    "frequent_items_3",
    "frequent_items_4",
    "frequent_items_5",
    "frequent_items_6",
    "frequent_items_7",
    "frequent_items_8",
    "frequent_items_9",
    "frequent_items_10",
    "frequent_items_11",
    "frequent_items_12",
    "frequent_items_13",
    "frequent_items_14",
    "frequent_items_15",
    "frequent_items_16",
    "frequent_items_17",
    "frequent_items_18"
  )
  
  
  # values
  value = c()
  for (i in columns) {
    value <- c(value, as.numeric(tdp[1, i]))
  }
  for (i in range(1, length(value) - 1)) {
    value[i] <- value[i] - value[i + 1]
  }
  
  
  data = data.frame(group,
                    subgroup,
                    value)
  
  data_ception = data.frame(
    s_group,
    s_group_1,
    s_group_2,
    s_group_3,
    s_group_4,
    s_group_5,
    s_group_6,
    s_group_7,
    s_group_8,
    s_group_9,
    s_group_10,
    s_group_11,
    s_group_12,
    s_group_13,
    s_group_14,
    s_group_15,
    s_group_16,
    s_group_17,
    subgroup,
    value
  )
  
  
  # OUTPUT
  output_file <-
    file.path(output_base_path,
              paste0(tools::file_path_sans_ext(basename(data_plot_path)), "_treemap.png"),
              fsep = '\\')
  
  png(filename = output_file,
      width = 1920,
      height = 1080)
  
  t = treemap(
    data,
    index = c("group",
              "subgroup"),
    vSize = "value",
    type = "index",
    title = "threshold:0.001",
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
        "_treemap_interactive.html"
      ),
      fsep = '\\'
    )
  interactive = d3tree2(t)
  htmlwidgets::saveWidget(interactive, output_file)
  
  t_ception = treemap(
    data_ception,
    index = c(
      "s_group",
      "s_group_1",
      "s_group_2",
      "s_group_3",
      "s_group_4",
      "s_group_5",
      "s_group_6",
      "s_group_7",
      "s_group_8",
      "s_group_9",
      "s_group_10",
      "s_group_11",
      "s_group_12",
      "s_group_13",
      "s_group_14",
      "s_group_15",
      "s_group_16",
      "s_group_17",
      "subgroup"
    ),
    vSize = "value",
    type = "depth",
    title = "threshold:0.001",
    align.labels = list(c("center", "center"),
                        c("center", "bottom"))
  )
  
  output_file <-
    file.path(
      output_base_path,
      paste0(
        tools::file_path_sans_ext(basename(data_plot_path)),
        "_treemap_interactive_nested.html"
      ),
      fsep = '\\'
    )
  interactive_nested = d3tree2(t_ception)
  htmlwidgets::saveWidget(interactive_nested,
                          output_file)
  return()
}

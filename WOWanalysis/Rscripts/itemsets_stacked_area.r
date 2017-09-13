library(scales)
library(tibble)
library(ggplot2)
library(pracma)

itemsets_stacked_area <-
  function(data_plot_path, output_base_path) {
    data_plot <- read.csv(data_plot_path)
    
    # data transformation
    tdp <- as_tibble(data_plot)
    # plotting stacked-area-graph
    
    # number of rows
    thresholds_num <- dim(tdp)[1]
    # number of frequent_itemsets_X fields
    baskets_num <- length(tdp[grep("frequent_itemsets_", names(tdp))])
    
    itemset_length <- sprintf("L%02d", seq(1,baskets_num))
    itemset_length <- rep(itemset_length, times = thresholds_num)
    
    threshold <- 0
    for (i in tdp["threshold"]) {
      for (j in i) {
        threshold <- c(threshold, (rep(as.character(j), times = baskets_num)))
        # X <- c(X, (rep(j, times = baskets_num)))
      }
    }
    threshold <- threshold[-1]
    
    frequent_itemsets_number <- 0
    for (i in 1:thresholds_num) {
      first_index <- grep("^frequent_itemsets_1$", colnames(tdp))
      last_index <-
        grep("^frequent_itemsets_1$", colnames(tdp)) + baskets_num - 1
      frequent_itemsets_number <- c(frequent_itemsets_number, as.numeric(tdp[i, first_index:last_index]))
    }
    frequent_itemsets_number <- frequent_itemsets_number[-1]
    
    my_data <- data.frame(itemset_length, threshold, frequent_itemsets_number)
    
    # OUTPUT settings
    o_width = 1920
    o_height = 1080
    base_output_file <-
      file.path(
        output_base_path,
        paste0(tools::file_path_sans_ext(basename(data_plot_path)), "_stacked_area"),
        fsep = '\\'
      )
    
    ## OUTPUT Default graph 
    output_file <-
      paste0(base_output_file,".png")
    
    png(filename = output_file,
        width = o_width,
        height = o_height)
    
    print(ggplot(my_data, aes(
      x = threshold,
      y = frequent_itemsets_number,
      group = itemset_length,
      fill = itemset_length
    )) + geom_area())
    
    dev.off()
    
    ## OUTPUT Y scaled as logaritm to avoid picks
    output_file <-
      paste0(base_output_file,"[log].png")
    
    png(filename = output_file,
        width = o_width,
        height = o_height)
    
    print(ggplot(my_data, aes(
      x = threshold,
      y = log1p(frequent_itemsets_number),
      group = itemset_length,
      fill = itemset_length
    )) + geom_area())
    
    dev.off()
    
    ## OUTPUT filled
    output_file <-
      paste0(base_output_file,"[filled].png")
    
    png(filename = output_file,
        width = o_width,
        height = o_height)
    
    print(ggplot(my_data, aes(
      x = threshold,
      y = frequent_itemsets_number,
      group = itemset_length,
      fill = itemset_length
    )) + geom_area(position = "fill"))
    
    dev.off()
    
    ## OUTPUT axis X transform (TO-FIX)
    # output_file <-
    #   paste0(base_output_file,"[x_scaled].png")
    # 
    # png(filename = output_file,
    #     width = o_width,
    #     height = o_height)
    # one_over = function()
    #   trans_new("one_over", function(x)
    #     nthroot(x, 10), function(x)
    #       nthroot(x, 10))
    # print(ggplot(my_data, aes(
    #   x = X,
    #   y = log1p(Y),
    #   group = itemset_length,
    #   fill = itemset_length
    # )) + geom_area() + coord_trans(x="one_over"))
    # dev.off()
    
    return()
  }

args = commandArgs(trailingOnly = TRUE)
if (length(args) == 2) {
  itemsets_stacked_area(args[1], args[2])
}



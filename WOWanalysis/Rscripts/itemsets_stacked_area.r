library(scales)
library(tibble)
library(ggplot2)
library(pracma)

# data import
data_plot_path <- "PATH"
data_plot <- read.csv(data_plot_path)

# data transformation
tdp <- as_tibble(data_plot)

# plotting stacked-area-graph

thresholds_num <- 11
baskets_num <- 18

Areas <- rep(c("S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18"),times = thresholds_num)

X <- 0
for(i in tdp["threshold"]){
  for(j in i){
    #X<- c(X,(rep(as.character(j), times=baskets_num)))
    X<- c(X,(rep(j, times=baskets_num)))
  }
}
X<- X[-1]

Y <- 0
for(i in 1:thresholds_num){
  Y <- c(Y,as.numeric(tdp[i,24:(24+18-1)]))
}
Y<- Y[-1]

my_data <- data.frame(Areas,X,Y)

# Default graph
ggplot(my_data, aes(x=X, y=Y, group=Areas, fill=Areas)) + geom_area()

# Y scaled as logaritm to avoid picks
ggplot(my_data, aes(x=X, y=log1p(Y), group=Areas, fill=Areas)) + geom_area()

# filled
ggplot(my_data, aes(x=X, y=Y, group=Areas, fill=Areas)) + geom_area(position="fill")

# axis X transform
one_over = function() trans_new("one_over", function(x) nthroot(x,10), function(x) nthroot(x,10))
ggplot(my_data, aes(x=X, y=log1p(Y), group=Areas, fill=Areas)) + geom_area() + coord_trans(x = "one_over")


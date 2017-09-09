library(gplots)

# data import

input_path <- "PATH"
m <- read.csv(input_path, header = FALSE)

# distance matrix
# d <- as.dist(t(as.matrix(m)), diag = TRUE, upper = TRUE)
d <- data.matrix(m)

# symmetric matrix
sym <- pmax(d, t(d), na.rm = TRUE)


# d <- as.dist(sym)

# dendogram
hc <- hclust(as.dist(sym))

## output

# Plot dendogram
# plot(hc)

# to PNG
png(filename = "output.png", width = 1920, height = 1080)

# heatmap
heatmap.2(sym, Rowv = as.dendrogram(hc), Colv = as.dendrogram(hc), symm = TRUE, trace="none")

dev.off()

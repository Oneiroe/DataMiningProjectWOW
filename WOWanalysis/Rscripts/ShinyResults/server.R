# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(plotly)

distances <- c('general',
               'appearance',
               'items',
               'mounts',
               'pets',
               'professions',
               'stats',
               'talents')

shinyServer(function(input, output) {
  output$distPlot <- renderPlot({
    # generate bins based on input$bins from ui.R
    x    <- faithful[, 2]
    bins <- seq(min(x), max(x), length.out = input$bins + 1)
    
    # draw the histogram with the specified number of bins
    hist(x,
         breaks = bins,
         col = 'darkgray',
         border = 'white')
    
  })
  
  ###########################################################
  # ITEMSETS STACKED AREA: SELECT IMAGE UNIQUE class/level/class&level/region
  output$plot_stacked_area <- renderImage({
    i_region <- input$regionItem
    i_level <- input$levelItem
    i_class <- input$classItem
    i_type <- input$area_type
    
    filename <- 'itemsets_unique'
    if (i_region == 'none') {
      if (i_level == 'all' & i_class == '0') {
        filename <- paste0(filename, '_global')
      }else{
        if (i_class != '0') {
          filename <- paste0(filename, '_c', i_class)
        }
        if (i_level != 'all') {
          filename <- paste0(filename, '_lv', i_level)
        }
      }
      
    } else{
      filename <- paste0('itemsets_unique_', i_region)
    }
    
    if (i_type == 'normal') {
      filename <- paste0(filename, "_stacked_area.png")
    } else{
      filename <- paste0(filename, "_stacked_area", i_type, ".png")
    }
    
    filepath <-
      normalizePath(file.path('www//images//itemsets', filename))
    # Return a list containing the filename
    list(src = filepath,
         style="width:100%",
         width = "auto",
         height = "auto"
         )
  }, deleteFile = FALSE)
  
  ###########################################################
  # ITEMSETS TREEMAP STATIC: SELECT IMAGE UNIQUE class/level/class&level/region and threshold
  output$plot_treemap <- renderImage({
    i_region <- input$regionItem
    i_level <- input$levelItem
    i_class <- input$classItem
    i_threshold <- input$threshold
    
    filename <- 'itemsets_unique'
    if (i_region == 'none') {
      if (i_level == 'all' & i_class == '0') {
        filename <- paste0(filename, '_global')
      }else{
      if (i_class != '0') {
        filename <- paste0(filename, '_c', i_class)
      }
      if (i_level != 'all') {
        filename <- paste0(filename, '_lv', i_level)
      }}
      
    } else{
      filename <- paste0('itemsets_unique_', i_region)
    }
    
    filename <- paste0(filename, "_treemap[", i_threshold, "].png")
    
    filepath <-
      normalizePath(file.path('www//images//itemsets', filename))
    # Return a list containing the filename
    list(src = filepath,
         width = 250,
         height = 250
         )
  }, deleteFile = FALSE)
  
  ###########################################################
  # ITEMSETS TREEMAP D3: SELECT IMAGE UNIQUE class/level/class&level/region and threshold
  output$plot_treemap_d3 <- renderUI({
    i_region <- input$regionItem
    i_level <- input$levelItem
    i_class <- input$classItem
    i_threshold <- input$threshold
    print(i_threshold)
    filename <- 'itemsets_unique'
    if (i_region == 'none') {
      if (i_level == 'all' & i_class == '0') {
        filename <- paste0(filename, '_global')
      }else{
      if (i_class != '0') {
        filename <- paste0(filename, '_c', i_class)
      }
      if (i_level != 'all') {
        filename <- paste0(filename, '_lv', i_level)
      }}
      
    } else{
      filename <- paste0('itemsets_unique_', i_region)
    }
    
    filename <- paste0(filename, "_treemap_interactive[", i_threshold, "].html")
    
    filepath <-
      normalizePath(file.path('www//images//itemsets', filename))
    # Return a list containing the filename
    list(includeHTML(filepath))
  })
  
  output$threshold_calculator <- renderText({ 
    as.character(input$threshNum*as.numeric(input$threshold))
  })
  
  ###########################################################
  # SIMILARITY UTILS
  select_heatmap_mpl <- function(i_region, i_level, i_class, i_distance) {
    filename <- 'sorted_matrix_unique'
    if (i_region == 'none') {
      # potentially you can avoid to check level
      if (i_level == 'all' & i_class == '0') {
        return()
      }
      if (i_class != '0') {
        filename <- paste0(filename, '_c', i_class)
      }
      if (i_level != 'all') {
        filename <- paste0(filename, '_lv', i_level)
      }
      
    } else{
      filename <- paste0(filename,'_', i_region)
    }
    
    filename <- paste0(filename, "[", i_distance, "]_heatmap_mpl.png")
    
    filepath <-
      normalizePath(file.path('www//images//similarity', filename))
    
    return(filepath)
  }
  
  select_heatmap_dendogram <- function(i_region, i_level, i_class, i_distance) {
    filename <- 'sorted_matrix_unique'
    if (i_region == 'none') {
      # potentially you can avoid to check level
      if (i_level == 'all' & i_class == '0') {
        return()
      }
      if (i_class != '0') {
        filename <- paste0(filename, '_c', i_class)
      }
      if (i_level != 'all') {
        filename <- paste0(filename, '_lv', i_level)
      }
      
    } else{
      filename <- paste0(filename,'_', i_region)
    }
    
    filename <- paste0(filename, "[", i_distance, "]_dendogrm_heatmap.png")
    
    filepath <-
      normalizePath(file.path('www//images//similarity', filename))
    
    return(filepath)
  }
  
  ###########################################################
  # SIMILARITY HEATMAP: SELECT IMAGE UNIQUE class/level/class&level/region
  output$plot_heatmap_mlp <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- input$distance_type
    
    filepath <- select_heatmap_mpl(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         # width = 700,
         # height = 700,
         # style = "width: 700px; height: 700px"
         style = "width:100%"
    )
  }, deleteFile = FALSE)
  
  output$plot_heatmap_dendogram <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- input$distance_type
    
    filepath <- select_heatmap_dendogram(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         # width = 700,
         # height = 700,
         # style = "width: 700px; height: 700px"
         style = "width:100%"
    )
  }, deleteFile = FALSE)
  
  ###########################################################
  # SIMILARITY HEATMAP GRID distances: SELECT IMAGE UNIQUE class/level/class&level/region
  output$plot_heatmap_mlp_grid_general <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'general'
    
    filepath <- select_heatmap_mpl(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  output$plot_heatmap_dendogram_grid_general <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'general'
    
    filepath <- select_heatmap_dendogram(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  
  output$plot_heatmap_dendogram_grid_appearance <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'appearance'
    
    filepath <- select_heatmap_dendogram(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  output$plot_heatmap_mlp_grid_appearance <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'appearance'
    
    filepath <- select_heatmap_mpl(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  
  output$plot_heatmap_mlp_grid_items <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'items'
    
    filepath <- select_heatmap_mpl(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  output$plot_heatmap_dendogram_grid_items <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'items'
    
    filepath <- select_heatmap_dendogram(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  
  output$plot_heatmap_mlp_grid_mounts <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'mounts'
    
    filepath <- select_heatmap_mpl(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  output$plot_heatmap_dendogram_grid_mounts <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'mounts'
    
    filepath <- select_heatmap_dendogram(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  
  output$plot_heatmap_mlp_grid_pets <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'pets'
    
    filepath <- select_heatmap_mpl(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  output$plot_heatmap_dendogram_grid_pets <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'pets'
    
    filepath <- select_heatmap_dendogram(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  
  output$plot_heatmap_mlp_grid_professions <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'professions'
    
    filepath <- select_heatmap_mpl(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  output$plot_heatmap_dendogram_grid_professions <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'professions'
    
    filepath <- select_heatmap_dendogram(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  
  output$plot_heatmap_mlp_grid_stats <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'stats'
    
    filepath <- select_heatmap_mpl(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  output$plot_heatmap_dendogram_grid_stats <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'stats'
    
    filepath <- select_heatmap_dendogram(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  
  output$plot_heatmap_mlp_grid_talents <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'talents'
    
    filepath <- select_heatmap_mpl(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)
  output$plot_heatmap_dendogram_grid_talents <- renderImage({
    i_region <- input$regionSimilarity
    i_level <- input$levelSimilarity
    i_class <- input$classSimilarity
    i_distance <- 'talents'
    
    filepath <- select_heatmap_dendogram(i_region, i_level, i_class, i_distance)
    # Return a list containing the filename
    list(src = filepath,
         width = 400,
         height = 400
    )
  }, deleteFile = FALSE)

  ###########################################################
  # SIMILARITY HEATMAP 3D
  output$plot_heatmap_3d <- renderUI({
    filepath <-
      normalizePath(file.path('www//images//similarity', 'similarity_3d_100x100_test.html'))
    
    # Return a list containing the filename
    list(includeHTML(filepath))
  })
})

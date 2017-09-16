# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)

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
        return()
      }
      if (i_class != '0') {
        filename <- paste0(filename, '_c', i_class)
      }
      if (i_level != 'all') {
        filename <- paste0(filename, '_lv', i_level)
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
         width = 400,
         height = 400
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
        return()
      }
      if (i_class != '0') {
        filename <- paste0(filename, '_c', i_class)
      }
      if (i_level != 'all') {
        filename <- paste0(filename, '_lv', i_level)
      }
      
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
        return()
      }
      if (i_class != '0') {
        filename <- paste0(filename, '_c', i_class)
      }
      if (i_level != 'all') {
        filename <- paste0(filename, '_lv', i_level)
      }
      
    } else{
      filename <- paste0('itemsets_unique_', i_region)
    }
    
    filename <- paste0(filename, "_treemap_interactive[", i_threshold, "].html")
    
    filepath <-
      normalizePath(file.path('www//images//itemsets', filename))
    # Return a list containing the filename
    list(includeHTML(filepath))
  })
  
  ###########################################################
  # SIMILARITY HEATMAP: SELECT IMAGE UNIQUE class/level/class&level/region
  output$plot_heatmap_mlp <- renderImage({
    i_region <- input$regionItem
    i_level <- input$levelItem
    i_class <- input$classItem
    i_distance <- input$distance_type
    
    filename <- 'sorted_matrix_unique'
    if (i_region == 'none') {
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
    # Return a list containing the filename
    list(src = filepath,
         width = 500,
         height = 500
    )
  }, deleteFile = FALSE)

})

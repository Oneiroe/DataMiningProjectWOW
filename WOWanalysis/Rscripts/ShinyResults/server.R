

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
  # GENDER: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_genders.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # REGIONS: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_regions_locales.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # RACES: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_races.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # CLASSES: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_classes.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # LEVELS LINES: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_levels_line.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # LEVELS BUBBLE: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_levels_bubble.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # GENDER: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_genders.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # GENDER: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_genders.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # GENDER: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_genders.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # GENDER: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_genders.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  ###########################################################
  # GENDER: SELECT IMAGE GLOBAL/UNIQUE 
  output$selected_uniq <- renderImage({
    filename <- normalizePath(file.path('www//images//stats',
                                        paste0(input$uniq, "_genders.png")))
    
    # Return a list containing the filename
    list(src = filename)
  }, deleteFile = FALSE)
  
  
})

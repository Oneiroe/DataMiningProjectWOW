# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)


regions <- c('none', 'EU', 'KR', 'TW', 'US')

levels <- c('all', '90', '100', '110')

classes <- as.character(seq(0, 12))

thresholds <-
  c(1, 0.75, 0.5, 0.25, 0.15, 0.1, 0.05, 0.01, 0.005, 0.002, 0.001)

distances <- c('general',
               'appearance',
               'items',
               'mounts',
               'pets',
               'professions',
               'stats',
               'talents')

stats_pages <- c('unique', 'globals')
stats_graphs <-
  c('genders',
    'regions_locales',
    'races',
    'classes',
    'levels_bubble',
    'levels_line')
ext_img <- '.png'

itemsets_stacked_area_types <- c('normal', '[filled]', '[log]')

shinyUI(
  fluidPage(
    ###########################################################
    # INTRO
    # Application title
    img(src = "images//DataArt//similarity_100x100_2.PNG", style = 'width:100%'),
    titlePanel("Data Mining Project WOW(!)"),
    img(src = "images//hdd_space_allocation.png", style = "width:100%"),
    ###########################################################
    # STATS
    h2("Stats"),
    tabsetPanel(
      tabPanel("unique",
               sidebarLayout(
                 sidebarPanel(p("EXPLANATION TEXT HERE")),
                 mainPanel(
                   h3("Gender"),
                   img(src = "images//stats//unique_genders.png"),
                   h3("Regions"),
                   img(src = "images//stats//unique_regions_locales.png"),
                   h3("Races"),
                   img(src = "images//stats//unique_races.png"),
                   h3("Classes"),
                   img(src = "images//stats//unique_classes.png"),
                   h3("Levels"),
                   img(src = "images//stats//unique_levels_line.png"),
                   # br(),
                   img(src = "images//stats//unique_levels_bubble.png"),
                   h3("Leveling Time"),
                   # img(src = "images//stats//unique_leveling_epoch.png", width=1000,eigth=1000),
                   img(src = "images//stats//unique_leveling_hours.png", width =
                         900, eigth = 900),
                   h3('Playtime'),
                   img(src = "images//stats//unique_playtime_years.png", width =
                         700, eigth = 700)
                 )
               )),
      tabPanel("global",
               sidebarLayout(
                 sidebarPanel(p("EXPLANATION TEXT HERE")),
                 mainPanel(
                   h3("Gender"),
                   img(src = "images//stats//globals_genders.png"),
                   h3("Regions"),
                   img(src = "images//stats//globals_regions_locales.png"),
                   h3("Races"),
                   img(src = "images//stats//globals_races.png"),
                   h3("Classes"),
                   img(src = "images//stats//globals_classes.png"),
                   h3("Levels"),
                   img(src = "images//stats//globals_levels_line.png"),
                   # br(),
                   img(src = "images//stats//globals_levels_bubble.png"),
                   h3("Leveling Time"),
                   # img(src = "images//stats//globals_leveling_epoch.png"),
                   img(src = "images//stats//globals_leveling_hours.png", width =
                         900, eigth = 900),
                   h3('Playtime'),
                   img(src = "images//stats//globals_playtime_years.png", width =
                         700, eigth = 700)
                 )
               ))
    ),
    img(src = "images//DataArt//similarity_100x100_1.PNG", style = 'width:100%'),
    ###########################################################
    # ITEMSETS
    h2("Itemsets"),
    
    sidebarLayout(
      sidebarPanel(
        selectInput(
          "classItem",
          label = "Select Class",
          choices = classes,
          selected = stats_pages[1]
        ),
        selectInput(
          "levelItem",
          label = "Select Level",
          choices = levels,
          selected = levels[1]
        ),
        p('or'),
        selectInput(
          "regionItem",
          label = "Select region",
          choices = regions,
          selected = regions[1]
        ),
        br(),
        selectInput(
          "area_type",
          label = "Kind of plot",
          choices = itemsets_stacked_area_types,
          selected = itemsets_stacked_area_types[1]
        ),
        br(),
        radioButtons(
          "threshold",
          label = "Threshold (%):",
          choices = thresholds,
          selected = thresholds[8]
        ),
        numericInput("threshNum", 
                     h3("Threshold Calculator"),
                     value = 10000),
        textOutput("threshold_calculator")
      ),
      mainPanel(
        ##############################
        # stacked area
        imageOutput("plot_stacked_area", height = "auto"),
        
        # ##############################
        # # treemap static
        # sidebarLayout(
        #   sidebarPanel(
        #     position = "right",
        #     radioButtons("threshold",
        #                  label = "Threshold (%):",
        #                  choices = thresholds)
        #   ),
        #   mainPanel(imageOutput("plot_treemap"))
        # )
        
        #############################
        # treemap D3
        uiOutput("plot_treemap_d3")
        
      )
    ),
    
    
    ###########################################################
    # SIMILARITY
    h2("Similarity"),
    sidebarLayout(
      sidebarPanel(
        selectInput(
          "classSimilarity",
          label = "Select Class",
          choices = classes,
          selected = stats_pages[1]
        ),
        selectInput(
          "levelSimilarity",
          label = "Select Level",
          choices = levels,
          selected = levels[1]
        ),
        p('or'),
        selectInput(
          "regionSimilarity",
          label = "Select region",
          choices = c('none', 'TW'),
          selected = 'TW'
        ),
        br(),
        selectInput(
          "distance_type",
          label = "Select distance measure",
          choices = distances,
          selected = distances[1]
        ),
        br(),
        p(
          'Note: dendogram only for class+level, excluding classes 2,5,7,11'
        )
      ),
      mainPanel(
        ##############################
        # heatmap
        
        fluidRow(
          imageOutput("plot_heatmap_mlp", height = "auto"),
          imageOutput("plot_heatmap_dendogram", height = "auto")
        ),
        # ##############################
        # # heatmap grid
        fluidRow(
          p('general'),
          imageOutput("plot_heatmap_mlp_grid_general", height = "auto"),
          imageOutput("plot_heatmap_dendogram_grid_general", height = "auto"),
          p('appearance'),
          imageOutput("plot_heatmap_mlp_grid_appearance", height = "auto"),
          imageOutput("plot_heatmap_dendogram_grid_appearance", height = "auto"),
          p('items'),
          imageOutput("plot_heatmap_mlp_grid_items", height = "auto"),
          imageOutput("plot_heatmap_dendogram_grid_items", height = "auto"),
          p('mounts'),
          imageOutput("plot_heatmap_mlp_grid_mounts", height = "auto"),
          imageOutput("plot_heatmap_dendogram_grid_mounts", height = "auto"),
          p('pets'),
          imageOutput("plot_heatmap_mlp_grid_pets", height = "auto"),
          imageOutput("plot_heatmap_dendogram_grid_pets", height = "auto"),
          p('professions'),
          imageOutput("plot_heatmap_mlp_grid_professions", height = "auto"),
          imageOutput("plot_heatmap_dendogram_grid_professions", height = "auto"),
          p('stats'),
          imageOutput("plot_heatmap_mlp_grid_stats", height = "auto"),
          imageOutput("plot_heatmap_dendogram_grid_stats", height = "auto"),
          p('talents'),
          imageOutput("plot_heatmap_mlp_grid_talents", height = "auto"),
          imageOutput("plot_heatmap_dendogram_grid_talents", height = "auto")
        )
        # h3("3D caption"),
        # uiOutput("plot_heatmap_3d")
      )
    ),
    ###########################################################
    # CONCLUSIONS
    
    ###########################################################
    # EXTRA
    h2("thanks for the attention!"),
    img(src = "images//DataArt//similarity_100x100_3.PNG", style = 'width:100%')
  )
  
)

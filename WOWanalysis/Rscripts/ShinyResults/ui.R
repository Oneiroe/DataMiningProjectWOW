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
    titlePanel("Data Mining Project WOW"),
    p('paragrafo'),
    p('paragraph 2'),
    sidebarLayout(
      position = "left",
      sidebarPanel("sidebar panel"),
      mainPanel("main panel")
    ),
    
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
    
    ###########################################################
    # ITEMSETS
    h2("Itemsets"),
    
    sidebarLayout(
      sidebarPanel(
        selectInput(
          "classItem",
          label = "Select Class",
          choices = classes,
          selected = stats_pages[2]
        ),
        selectInput(
          "levelItem",
          label = "Select Level",
          choices = levels,
          selected = levels[2]
        ),
        p('or'),
        selectInput(
          "regionItem",
          label = "Select region",
          choices = regions,
          selected = regions[2]
        )
      ),
      mainPanel(
        ##############################
        # stacked area
        sidebarLayout(
          sidebarPanel(
            position = "right",
            selectInput(
              "area_type",
              label = "Kind of plot",
              choices = itemsets_stacked_area_types,
              selected = itemsets_stacked_area_types[1]
            )
          ),
          mainPanel(imageOutput("plot_stacked_area"))
        ),
        
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
        sidebarLayout(
          sidebarPanel(
            position = "right",
            radioButtons("threshold",
                         label = "Threshold (%):",
                         choices = thresholds)
          ),
          mainPanel(
            uiOutput("plot_treemap_d3")
          )
        )
      )
    ),
    
    
    ###########################################################
    # SIMILARITY
    h2("Similarity"),
    sidebarLayout(
      sidebarPanel(),
      mainPanel(
        ##############################
        # heatmap
        sidebarLayout(
          sidebarPanel(
            position = "right",
            selectInput(
              "distance_type",
              label = "Select distance measure",
              choices = distances,
              selected = distances[1]
            )
          ),
          mainPanel(imageOutput("plot_heatmap_mlp"))
        )
        ,
        # ##############################
        # # heatmap grid
        p('general'),
        imageOutput("plot_heatmap_mlp_grid_general"),
        p('appearance'),
        imageOutput("plot_heatmap_mlp_grid_appearance"),
        p('items'),
        imageOutput("plot_heatmap_mlp_grid_items"),
        p('mounts'),
        imageOutput("plot_heatmap_mlp_grid_mounts"),
        p('pets'),
        imageOutput("plot_heatmap_mlp_grid_pets"),
        p('professions'),
        imageOutput("plot_heatmap_mlp_grid_professions"),
        p('stats'),
        imageOutput("plot_heatmap_mlp_grid_stats"),
        p('talents'),
        imageOutput("plot_heatmap_mlp_grid_talents")
      )
    ),
    ###########################################################
    # CONCLUSIONS
    
    ###########################################################
    # EXTRA
    h2("DataArt")
  )
  
)

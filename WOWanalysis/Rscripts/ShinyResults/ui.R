

# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)


regions <- c('EU', 'KR', 'TW', 'US')

levels <- c('90', '100', '110')

class <- as.character(seq(1, 12))

distances <- c('general',
               'appearance',
               'items',
               'mounts',
               'pets',
               'professions',
               'stats',
               'talents')

stats_pages <- c('unique','globals')
stats_graphs <- c('genders','regions_locales','races','classes','levels_bubble','levels_line')
ext_img <- '.png'

shinyUI(fluidPage(
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

h2("TEST"),
# tabsetPanel(tabPanel("tab1",
#                      sidebarLayout(
#                        sidebarPanel(
#                          selectInput(
#                            "uniq",
#                            label = "Duplications?",
#                            choices = stats_pages,
#                            selected = stats_pages[1]
#                          )
#                        ),
#                        mainPanel(imageOutput("selected_uniq"))
#                      )),
#             tabPanel("tab2", h4('carramba'))
# ),
  

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
               h3("Playtime"),
               # img(src = "images//stats//unique_leveling_epoch.png", width=1000,eigth=1000),
               img(src = "images//stats//unique_leveling_hours.png", width =
                     900, eigth = 900),
               h3('Leveling Time'),
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
               h3("Playtime"),
               # img(src = "images//stats//globals_leveling_epoch.png"),
               img(src = "images//stats//globals_leveling_hours.png", width =
                     900, eigth = 900),
               h3('Leveling Time'),
               img(src = "images//stats//globals_playtime_years.png", width =
                     700, eigth = 700)
             )
           ))
),

###########################################################
# ITEMSETS
  h2("Itemsets"),


###########################################################
# SIMILARITY
  h2("Similarity"),
  
  

  # Sidebar with a slider input for number of bins
  sidebarLayout(sidebarPanel(
    sliderInput(
      "bins",
      "Number of bins:",
      min = 1,
      max = 50,
      value = 30
    )
  ),
  
  # Show a plot of the generated distribution
  mainPanel(plotOutput("distPlot")))
))

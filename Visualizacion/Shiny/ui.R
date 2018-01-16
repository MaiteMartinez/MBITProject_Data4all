library(shiny)
library(readxl)

df1=read_excel("C:/Users/Silvia/Desktop/Proyecto/Detect_Pers/Colgado Git Hub/Filtro_pers.xlsx")
View(df1)
df2=read_excel("C:/Users/Silvia/Desktop/Proyecto/Detect_Pers/Colgado Git Hub/Filtro_pers.xlsx")



ui <- fluidPage(
  title = "Ranking de candidatos",
  sidebarLayout(
    sidebarPanel(
      conditionalPanel(
        'input.dataset === "df1"',
        checkboxGroupInput("show_vars", "Datos que desea inspeccionar:",
                           names(df1), selected = names(df1))
      ),
      
      conditionalPanel(
        'input.dataset === "df2"',
        helpText ("Muestra los 5 primeros")
      )
      
      
      ),
      
    mainPanel(
      tabsetPanel(
        id = 'dataset',
        tabPanel("df1", DT::dataTableOutput("mytable1")),
        tabPanel("df2", DT::dataTableOutput("mytable2"))
        
      )
    )
  )
)

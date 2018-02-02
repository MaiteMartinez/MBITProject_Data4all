library(shiny)
library(readxl)
library(shinyBS)
library(DT)
library(networkD3)
library(dplyr)

options(digits=5)

nodos = read.csv("C:/Users/Silvia/Documents/GitHub/MBITProject_Data4all/Python/tables/relations_graph [Nodes].csv", 
                 header = TRUE, sep = ",")

MisNodos = nodos[,c(1,2)]
vertices = read.csv("C:/Users/Silvia/Documents/GitHub/MBITProject_Data4all/Python/tables/relations_graph [Edges].csv", 
                    header = TRUE, sep = ",")

MisVertices = vertices [,c(1,2)]

data_cent = read_excel("C:/Users/Silvia/Documents/GitHub/MBITProject_Data4all/Python/tables/4_ranked_users.xlsx")
data_cent$user_id = as.numeric(data_cent$user_id)

#nodos <- data_cent %>% left_join(nodos, by = c("user_id" = "label"))
nodos <- nodos %>% left_join(data_cent, by = c("label"="user_id" ))

MisNodos <- nodos[ , c(1,2,10,15,16,17,18,19,20,21,22)]

MisNodos[3:11] <- lapply(MisNodos[3:11], as.numeric)

MisNodos$degree = round(MisNodos$degree,3)
MisNodos$in_degree = round(MisNodos$in_degree,3)
MisNodos$out_degree = round(MisNodos$out_degree,3)
MisNodos$eigenvector = round(MisNodos$eigenvector,3)
MisNodos$katz_bonacich = round(MisNodos$katz_bonacich,3)
MisNodos$pagerank = round(MisNodos$pagerank,3)
MisNodos$closeness = round(MisNodos$closeness,3)
MisNodos$betweenness = round(MisNodos$betweenness,3)

MisNodos_g = cbind(MisNodos,"")
MisNodos_g$description <- paste("User_id:", MisNodos_g$label,
                                "Degree:", MisNodos_g$degree,
                                "In_degree:",MisNodos_g$in_degree,
                                "Out_degree:",MisNodos_g$out_degree,
                                "Eigenvector:",MisNodos_g$eigenvector,
                                "Katz_bonacich:",MisNodos_g$katz_bonacich,
                                "Pagerank:",MisNodos_g$pagerank,
                                "Closeness:",MisNodos_g$closeness,
                                "Betweenness:",MisNodos_g$betweenness)





# UI
ui <- fluidPage(theme = "bootstrap.css",
  titlePanel("Ranking de candidatos"),
  
  
  #actionButton("do", "Mostrar Grafo", icon = icon("play-circle")), # boton para que al pular salga grafo
  
  tags$head(tags$style(HTML('#add{background-color:orange}'))),
  
  bsModal("modalnew", "Introduce porcentajes para ponderar el resultado", "add", size = "large",
          #tags$head(tags$style(HTML('#modalnew{color:orange}'))),
          HTML(paste0("<div style='color:","red","'>",
                      paste0("<b>","La suma de los valores introducidos debe ser 100"),
                      "</div>")),
          br(),
          fluidRow(column(4,numericInput(inputId = "Id", label="h_index", value = 0, step = 5,width = '60%')),
                   column(4, numericInput(inputId = "C1", label="Degree ", value = 0, step = 5,width = '60%')),
                   column(4, numericInput(inputId = "C2", label="In_degree ", value = 0, step = 5,width = '60%')),
                   br(),
                   column(4,numericInput(inputId = "C3", label="Out_degree ", value = 0, step = 5,width = '60%')),
                   column(4, numericInput(inputId = "C4", label="Eigenvector ", value = 0, step = 5,width = '60%')),
                   column(4, numericInput(inputId = "C5", label="Katz_Bonacich ", value = 0, step = 5,width = '60%')),
                   br(),
                   column(4,numericInput(inputId = "C6", label="Out_degree ", value = 0, step = 5,width = '60%')),
                   column(4, numericInput(inputId = "C7", label="PageRank ", value = 0, step = 5,width = '60%')),
                   column(4,numericInput(inputId = "C8", label="Closeness ", value = 0, step = 5,width = '60%')),
                   br(),
                   column(4,numericInput(inputId = "C9", label="Betweeness ", value = 0, step = 5,width = '60%'))),
                      
          br(),
          HTML(paste0("<div style='color:","grey","'>",
                      paste0("Pulsa 'Calcular' y cierre la ventana para ver el resultado"),
                      "</div>")),
          br(),
          actionButton("butt", "Calcular"),
          tags$head(tags$style(HTML('#butt{background-color:LightGray}')))),
          
              tags$style(type='text/css', '#mensaje {background-color: rgba(255,255,0,0.40); color: red;}'),
              h3(textOutput(outputId = "mensaje", container = span)),
  
  tabsetPanel(
            
            tabPanel("Listado de candidatos",
                   
                     fluidRow(column(5,"    "),
                              column(5, actionButton("add", "Pondera el resultado"))),
                     br(),
                     DT::dataTableOutput("mytable1")), # muestre la tabla )
  
            tabPanel("Grafo", 
                     fluidRow(
                       column(5,"El tamano y el color de los nodos es funcion del h_index"),
                       column(10, forceNetworkOutput(outputId = "grafo")),
                       column(1, textOutput("text"))
                     )
            )
                     
           
           
  )
  )



  



#server.R
server<-function(input,output,session) {
  
  MisNodos_g$group <- MisNodos_g$h_index
  MisNodos_g$nodesize <- as.character((MisNodos_g$h_index) * 50)
  
  output$grafo <- renderForceNetwork({
    fn <- forceNetwork(
    Links = MisVertices, Nodes = MisNodos_g, 
    Source = "Source",
    Target = "Target",
    NodeID ="label",
    Group = "group",
    #Value = "width",
    opacity = 9,
    zoom = TRUE,
    fontSize =13,
    height = NULL, width = NULL,
    Nodesize = "nodesize",
    linkDistance = 5,
    charge = -5,
    legend = TRUE,
    bounded = FALSE,
    clickAction = "Shiny.onInputChange('id', d.description);"  )
  fn$x$nodes$description <- MisNodos_g$description
  fn
  })
  
  output$text <- renderPrint({ input$id })
  
  
  
  
  x <- eventReactive(input$butt, {
    input$Id + input$C1 + input$C2 + input$C3 + input$C4 + input$C5 + input$C6 + input$C7 + input$C8 + input$C9 
    })
  
  
  observeEvent(input$butt, {
    if (x()!=100){
    showModal(modalDialog(
      HTML(paste0("<div style='color:","black","'>",
                  paste0("<b>","Revisa los datos introducidos.<br/>
                         La suma debe ser 100"),
                  "</div>")),
      easyClose = TRUE
    ))
    }
  })
  
  output$mensaje <- renderText({
    if(x()==100){
      ""
    } else ({paste0("La suma de los Porcentajes no suma 100%")})
  })
  
  
  
  # Imprima el dataframe
  output$mytable1 <- DT::renderDataTable({
    
    
            DT::datatable(add_to_MisNodos(), 
                      escape=FALSE,
                      colnames = c(HTML('<span title ="Introduce texto 2">N</span>') , 
                                   HTML('<span title ="Introduce texto 2">Id</span>') ,
                                   HTML('<span title ="Introduce texto 3">User_id</span>'),
                                   HTML('<span title ="Introduce texto 4">h_index</span>'),
                                   HTML('<span title ="Introduce texto 4">Degree</span>'),
                                   HTML('<span title ="Introduce texto 4">In_degree</span>'),
                                   HTML('<span title ="Introduce texto 4">Out_degree</span>'),
                                   HTML('<span title ="Introduce texto 4">Eigenvector</span>'),
                                   HTML('<span title ="Introduce texto 4">Katz_bonacich</span>'),
                                   HTML('<span title ="Introduce texto 4">Pagerank</span>'),
                                   HTML('<span title ="Introduce texto 4">Closeness</span>'),
                                   HTML('<span title ="Introduce texto 4">Betweenness</span>'),
                                   HTML('<span title ="Introduce texto 4">Resultado</span>')
                                   ),
                      options = list(searching = FALSE,
                                     initComplete = JS(
                                       "function(settings, json) {",
                                       "$(this.api().table().header()).css({'background-color': '	#575757', 'color': '#fff'});",
                                       "}")
                                     ))
        })
  
    New_column<- reactive({ 
      column <- ( MisNodos$h_index*input$Id/100000 +
                  as.numeric(MisNodos$degree)*input$Id/100 +
                  as.numeric(MisNodos$in_degree)*input$Id/100 + 
                  as.numeric(MisNodos$out_degree)*input$Id/100 +
                  as.numeric(MisNodos$eigenvector)*input$Id/100 + 
                  as.numeric(MisNodos$katz_bonacich)*input$Id/100 +
                  as.numeric(MisNodos$pagerank)*input$Id/100 + 
                  as.numeric(MisNodos$closeness)*input$Id/100 +
                  as.numeric(MisNodos$betweenness)*input$Id/100 )
      column
      })
    # Incluyo la nueva columna "resultado" en el dataframe
    add_to_MisNodos <- reactive({
        MisNodos$resultado<- NA
        nRows <- nrow(MisNodos)
        MisNodos$resultado <- New_column()
        MisNodos
        }) 
  
}

shinyApp(ui = ui, server = server)
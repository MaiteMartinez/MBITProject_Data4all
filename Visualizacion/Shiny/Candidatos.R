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

# Calculas valores minimo y maximo para posteriormente normalizar a 0-1

# Minimos
Min_h_index = min(MisNodos$h_index,na.rm=T)
Min_degree = min(MisNodos$degree,na.rm=T)
Min_in_degree = min(MisNodos$in_degree,na.rm=T)
Min_out_degree = min(MisNodos$out_degree,na.rm=T)
Min_eigenvector = min(MisNodos$eigenvector,na.rm=T)
Min_katz_bonacich = min(MisNodos$katz_bonacich,na.rm=T)
Min_pagerank = min(MisNodos$pagerank,na.rm=T)
Min_closeness = min(MisNodos$closeness,na.rm=T)
Min_betweenness = min(MisNodos$betweenness,na.rm=T)

#Maximos
den_h_index = max(MisNodos$h_index, na.rm=T) - Min_h_index
den_degree = max(MisNodos$degree, na.rm=T) - Min_degree
den_in_degree = max(MisNodos$in_degree, na.rm=T) - Min_in_degree
den_out_degree = max(MisNodos$out_degree, na.rm=T) - Min_out_degree
den_eigenvector = max(MisNodos$eigenvector, na.rm=T) - Min_eigenvector
den_katz_bonacich = max(MisNodos$katz_bonacich, na.rm=T) - Min_katz_bonacich
den_pagerank = max(MisNodos$pagerank, na.rm=T) - Min_pagerank
den_closeness = max(MisNodos$closeness, na.rm=T) - Min_closeness
den_betweenness = max(MisNodos$betweenness, na.rm=T) - Min_betweenness



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
                      colnames = c(HTML('<span title ="">N</span>') , 
                                   HTML('<span title ="">Id</span>') ,
                                   HTML('<span title ="Id del usuario">User_id</span>'),
                                   HTML('<span title ="Sistema propuesto para la medicion de la calidad profesional de fisicos y de otros cientificos,
                                        en funcion de la cantidad de citas que han recibido sus articulos cientificos. 
                                        Un cientifico tiene indice h si ha publicado h trabajos con al menos h citas 
                                        cada uno.">h_index</span>'),
                                   HTML('<span title ="El grado (degree) de un nodo n es el numero 
                                        de aristas incidentes en n.">Degree</span>'),
                                   HTML('<span title ="Numero de aristas que apuntan a n, 
                                        en nuestro caso el numero de followers. 
                                        Representaria la capacidad de liderazgo del usuario">In_degree</span>'),
                                   HTML('<span title ="Numero de aristas que parten de n, 
                                        en nuestro caso, el numero de usuarios a los que sigue n">Out_degree</span>'),
                                   HTML('<span title ="Es una extension del concepto de centralidad por grado que captura la intuicion de que la importancia
                                        de un nodo en la red incrementa por el hecho de 
                                        estar conectado a otros nodos a su vez relevantes.">Eigenvector</span>'),
                                   HTML('<span title ="Tiene en cuenta la relaciÃ³n directa e indirecta de un nodo con el resto
                                        de nodos de la red penalizÃ¡ndolos a medida que crece la distacia.">Katz_bonacich</span>'),
                                   HTML('<span title ="La idea de PageRank es repartir la centralidad
                                        aportada por un nodo entre todos aquellos a los que apunta, de tal forma que cada uno de ellos
                                        recibira solo la parte proporcional de la centralidad del nodo de partida, esto es, la centralidad del
                                        nodo dividida por su out-degree (numero de enlaces salientes):">Pagerank</span>'),
                                   HTML('<span title ="En un grafo conexo, la cercana (closeness) de un nodo es el inverso de la suma de las 
                                        longitudes de los caminos minimos que unen dicho nodo con todos 
                                        los demas:">Closeness</span>'),
                                   HTML('<span title ="Captura en que medida un nodo esta situado en los caminos que unen a otros nodos. Los nodos
                                        con una intermediacion alta pueden tener mucha influencia en la red, dado que 
                                        controlan la informacion que se transmite entre otros nodos. Tambien son nodos que si desaparecieran impediran
                                        la transmision de la informacion y aumentara la desconexion de la red.">Betweenness</span>'),
                                   HTML('<span title ="PonderaciÃ³n de todos los Ã­ndices">Resultado</span>')
                                   ),
                      options = list(searching = TRUE,
                                     initComplete = JS(
                                       "function(settings, json) {",
                                       "$(this.api().table().header()).css({'background-color': '	#575757', 'color': '#fff'});",
                                       "}")
                                     ))
        })
  
    New_column<- reactive({ 
      # Para ponderar tenemos que normalizar los datos al encontrarse en diferentes escalas
      column <- ( round((MisNodos$h_index - Min_h_index)*input$Id/(den_h_index)  +
                  (MisNodos$degree - Min_degree)*input$Id/(den_degree)  +
                  (MisNodos$in_degree - Min_in_degree)*input$Id/(den_in_degree)  +
                  (MisNodos$out_degree - Min_out_degree)*input$Id/(den_out_degree)  +
                  (MisNodos$eigenvector - Min_eigenvector)*input$Id/(den_eigenvector)  +
                  (MisNodos$katz_bonacich - Min_katz_bonacich)*input$Id/(den_katz_bonacich)  +
                  (MisNodos$pagerank - Min_pagerank)*input$Id/(den_pagerank*100)  +
                  (MisNodos$closeness - Min_closeness)*input$Id/(den_closeness*100)  +
                  (MisNodos$betweenness - Min_betweenness)*input$Id/(den_betweenness*100),3)  )
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
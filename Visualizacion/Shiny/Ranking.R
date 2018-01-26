library(shiny)
library(readxl)
library(shinyBS)


df1=read_excel("C:/Users/Silvia/Desktop/Proyecto/Detect_Pers/Colgado Git Hub/Filtro_pers.xlsx")
#View(df1)


# UI
ui <- fluidPage(
  titlePanel("Ranking de candidatos"),
  actionButton("do", "Mostrar Grafo", icon = icon("play-circle")), # boton para que al pular salga grafo
  actionButton("add", "Pondera el resultado"),
  tags$head(tags$style(HTML('#add{background-color:orange}'))),
  bsModal("modalnew", "Introduce porcentajes para ponderar el resultado", "add", size = "large",
          tags$head(tags$style(HTML('#modalnew{color:orange}'))),
          HTML(paste0("<div style='color:","red","'>",
                      paste0("<b>","La suma de los valores introducidos debe ser 100"),
                      "</div>")),
          br(),
          splitLayout(cellWidths = c("20%", "20%","20%","20%"),
                      numericInput(inputId = "Id", label="h_index", value = 0, step = 5,width = '75%'),
                      numericInput(inputId = "C1", label="Centralidad_1 ", value = 0, step = 5,width = '75%'),
                      numericInput(inputId = "C2", label="Centralidad_2 ", value = 0, step = 5,width = '75%'),
                      numericInput(inputId = "C3", label="Centralidad_3 ", value = 0, step = 5,width = '75%')
                      ),
          br(),
          actionButton("butt", "Calcula")
          
  ),
  mainPanel( h3(textOutput(outputId = "mensaje", container = span)),
              DT::dataTableOutput("mytable1") # muestre la tabla 
  )
)


#server.R
server<-function(input,output,session) {
  
  
  x <- eventReactive(input$butt, {
    input$Id + input$C1 + input$C2 + input$C3
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
    } else ("La suma de los Porcentajes no suma 100%")
  })
  
  
  # Imprima el dataframe
  output$mytable1 <- DT::renderDataTable({
        DT::datatable(add_to_df1(),options = list(searching = FALSE))
        })
  
    New_column<- reactive({ 
      column <- (df1$user.id*input$Id/100) # las operaciones a realizar para el cálculo final. HABRIA QUE METER MÄS SUMANDOS
      column
      })
    # Incluyo la nueva columna "resultado" en el dataframe
    add_to_df1 <- reactive({
        df1$resultado<- NA
        nRows <- nrow(df1)
        df1$resultado <- New_column()
        df1
        }) 
  
}

shinyApp(ui = ui, server = server)
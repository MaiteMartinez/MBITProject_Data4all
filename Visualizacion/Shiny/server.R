library(shiny)


server <- function(input, output) {
  
  # choose columns to display
  dfr = df1[sample(nrow(df1), 1000), ]
  
  output$mytable1 <- DT::renderDataTable({
    DT::datatable(dfr[, input$show_vars,drop = FALSE],
                  filter="top", selection="multiple", escape=FALSE,
                  options = list (lenghtMenu = c(5,10,20,50), pageLenght = 10, searching = FALSE)
                      )
  })
  
  
  output$mytable2 <- DT::renderDataTable({
    DT::datatable(df2, options = list (lenghtMenu = c(5,30,50), pageLenght = 5))
  })
  
  
}


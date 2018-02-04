library(openxlsx)

rm(list=ls())

ruta_datos = "C:/DATOS/MBIT/Proyecto/MBITProject_Data4all/Python/tables/4_ranked_users.xlsx"

# Leemos los datos.

datos = read.xlsx(xlsxFile=ruta_datos, sheet = 1) 

col_names=c("user_id", 
                  "h_index",
                  "degree",
                  "in_degree",
                  "out_degree",
                  "eigenvector",
                  "katz_bonacich",
                  "pagerank",
                  "closeness",
                  "betweenness"
)

datos = datos[col_names]
datos[, "h_index"] <- sapply(datos[, "h_index"], as.integer)
summary(datos)

hist(datos[, "h_index"],  breaks=20)


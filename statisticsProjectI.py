import numpy as np 
import pandas as pd
import matplotlib.pyplot  as plt
import seaborn; seaborn.set()
import openpyxl;
#data.columns
#Index(['Libro', 'Titulo del libro', 'Especialidad', 'Opinión del 1 al 6'], dtype='object')

data = pd.read_csv("BooksProject.csv")
 
describeTable = data.groupby(['Libro'])['Opinión del 1 al 6'].describe().reset_index()
describeTable.set_index(['Libro','count','mean','std','50%'], inplace = True)
describeTable.drop(columns = describeTable.columns, inplace = True)
groupedEspecialtyBooks = data.groupby(['Libro', 'Especialidad']).size()
#3) book valorations distributions
opinionsfi = data.groupby(['Libro', 'Opinión del 1 al 6']).size()
#print(opinionsfi.index.levels[1].values)
missingVal = {}
fiColumns = ['Libro','Opinión del 1 al 6','fi'] 
for col in fiColumns:
  missingVal[col] = []
  
#create a dictionary with the books-rates info that are not present as a row (0 students given an x rating to a y book), adding a fi (absolute frecuency) of 0. 
#crear un diccionario con la información de libros-valoraciones que no están presentes como filas (0 estudiantes dando una valoración x a un libro y),
#añadiendo una fi (frecuencia absoluta) 0

#E.G: { 'Libro' : [2,3,4], 'Opinión del 1 al 6': [1,1,2], 'fi': [0,0,0]
for book in opinionsfi.index.levels[0].values:
  for val in opinionsfi.index.levels[1].values:
    j = (data[fiColumns[0]] == book) & (data[fiColumns[1]] == val)
    if(not j.any()):
      missingVal[fiColumns[0]].append(book)
      missingVal[fiColumns[1]].append(val)
      missingVal[fiColumns[2]].append(0)

nonPresentVal = pd.DataFrame(missingVal, columns = fiColumns)
opinionshi = opinionsfi / opinionsfi.groupby(['Libro']).sum()  * 100
bookRatesDistributions = opinionsfi.to_frame('fi').reset_index()
bookRatesDistributions = pd.concat([bookRatesDistributions,nonPresentVal]).sort_values(by=['Libro', 'Opinión del 1 al 6'])
bookRatesDistributions.set_index(['Libro', 'Opinión del 1 al 6'], inplace = True)
bookRatesDistributions['hi'] = opinionshi
bookRatesDistributions['Fi'] = opinionsfi.groupby(['Libro']).cumsum()
bookRatesDistributions['Hi'] = opinionshi.groupby(['Libro']).cumsum()

# to this columns fill 0's int the rows that were added because of no records for a book rate
# llenar estas columnas con 0's en las filas que fueron añadidas debido a que su valoración no poseía registros
bookRatesDistributions['hi'].fillna(0, inplace = True) 
bookRatesDistributions['Fi'].fillna(0, inplace = True) 
bookRatesDistributions['Hi'].fillna(0, inplace = True) 

# join the general information
finalTable = describeTable.join(bookRatesDistributions, how='inner').sort_index(axis = 0)
finalTable.to_csv('out.csv', index=True)
finalTable.to_excel("output.xlsx")  

bins = np.arange(1,7)
# plt.hist(bookARatings,bins)
# plt.hist(bookBRatings,bins)
# plt.show()

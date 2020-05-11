import numpy as np 
import pandas as pd
import matplotlib.pyplot  as plt
import seaborn; seaborn.set()
import openpyxl;
#data.columns
#Index(['Libro', 'Titulo del libro', 'Especialidad', 'Opinión del 1 al 6'], dtype='object')
data = pd.read_csv("BooksProject.csv")
data.dropna(subset= ['Especialidad','Libro','Opinión del 1 al 6'], inplace=True)
dataIndexes = ['Especialidad','Libro','Número de Valoraciones','Media','Cuasidesviación','Mediana', 'Moda']

bookGroupedRates = data.groupby(['Especialidad','Libro'])['Opinión del 1 al 6']
describeTable = bookGroupedRates.describe().reset_index()
firstLevelModes = bookGroupedRates.apply(lambda x: x.mode().iloc[0]).reset_index().rename(columns={'Opinión del 1 al 6': 'Moda'})
describeTable = pd.merge(describeTable, firstLevelModes,  how='left', left_on=['Especialidad','Libro'], right_on = ['Especialidad','Libro'])
describeTable.rename(columns={'count': 'Número de Valoraciones','mean':'Media', 'std':'Cuasidesviación','50%': 'Mediana'}, inplace=True)
describeTable.set_index(dataIndexes, inplace = True)
describeTable.drop(columns = describeTable.columns, inplace = True)
#3) book valorations distributions
opinionsfi = data.groupby(['Especialidad','Libro', 'Opinión del 1 al 6']).size()
#print(opinionsfi.index.levels[1].values)
missingVal = {}
especialtyBooks = {}
fiColumns = ['Especialidad','Libro','Opinión del 1 al 6','fi'] 
for col in fiColumns:
  missingVal[col] = []
  
#create a dictionary with the books-rates info that are not present as a row (0 students given an x rating to a y book), adding a fi (absolute frecuency) of 0. 
#crear un diccionario con la información de libros-valoraciones que no están presentes como filas (0 estudiantes dando una valoración x a un libro y),
#añadiendo una fi (frecuencia absoluta) 0

#E.G: { 'Libro' : [2,3,4], 'Opinión del 1 al 6': [1,1,2], 'fi': [0,0,0]

for book in opinionsfi.index.levels[1].values:
  especialty = data[data[fiColumns[1]] == book][fiColumns[0]].iloc[0]
  if(not especialty in especialtyBooks):
    especialtyBooks[especialty] = []
  especialtyBooks[especialty].append(book)
  for val in np.arange(1,7):
    j = (data[fiColumns[1]] == book) & (data[fiColumns[2]] == val)
    if(not j.any()):
      missingVal[fiColumns[0]].append(data[data[fiColumns[1]] == book][fiColumns[0]].iloc[0])
      missingVal[fiColumns[1]].append(book)
      missingVal[fiColumns[2]].append(val)
      missingVal[fiColumns[3]].append(0)

nonPresentVal = pd.DataFrame(missingVal, columns = fiColumns)

opinionshi = opinionsfi / opinionsfi.groupby(['Especialidad','Libro']).sum()  * 100

bookRatesDistributions = opinionsfi.to_frame('fi').reset_index()
bookRatesDistributions = pd.concat([bookRatesDistributions,nonPresentVal]).sort_values(by=['Especialidad','Libro', 'Opinión del 1 al 6'])
bookRatesDistributions.set_index(['Especialidad','Libro', 'Opinión del 1 al 6'], inplace = True)
bookRatesDistributions['hi'] = opinionshi
bookRatesDistributions['Fi'] = opinionsfi.groupby(['Especialidad','Libro']).cumsum()
bookRatesDistributions['Hi'] = opinionshi.groupby(['Especialidad','Libro']).cumsum()

# to this columns fill 0's int the rows that were added because of no records for a book rate
# llenar estas columnas con 0's en las filas que fueron añadidas debido a que su valoración no poseía registros
bookRatesDistributions['hi'].fillna(0, inplace = True) 
bookRatesDistributions['Fi'].fillna(0, inplace = True) 
bookRatesDistributions['Hi'].fillna(0, inplace = True) 
# join the general information
finalTable = describeTable.join(bookRatesDistributions, how='inner')
finalTable.set_index(finalTable.index.reorder_levels([*dataIndexes, 'Opinión del 1 al 6']), inplace = True)
finalTable.sort_values(by=['Especialidad','Número de Valoraciones','Opinión del 1 al 6'], inplace = True, ascending = [True,False, True])
finalTable.to_excel("output.xlsx")  

fisByEspecialty = [[data[data['Libro'] == book]['Opinión del 1 al 6'].values  for book in especialtyBooks[especialty]] for especialty in especialtyBooks]
labels = [[especialty, especialtyBooks[especialty]] for especialty in especialtyBooks]

# [[data[data['Libro'] == book]['Opinión del 1 al 6'].values
bins = np.arange(0, 6 + 1.5) - 0.5
for i in range(len(especialtyBooks)):
  fig, ax = plt.subplots()
  _ = ax.hist(fisByEspecialty[i], bins, density = True, label = labels[i][1])
  ax.set_xticks(bins + 0.5)
  ax.legend(prop={'size': 10})
  ax.set_title(labels[i][0])
  plt.figure(i)
  i+=1
plt.close(0)
plt.show()
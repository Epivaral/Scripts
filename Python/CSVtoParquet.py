# https://github.com/Epivaral/scripts

# Simple script to convert .csv file to .parquet
# The file is created on the same directory as the source


import pandas as pd


inputFileName = input("CSV file to convert: >>>>")
outputFileName = inputFileName.replace('.csv', '.parquet')

df = pd.read_csv(inputFileName)
df.to_parquet(outputFileName)

print('File successfully created at: ', outputFileName)

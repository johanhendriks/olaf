#!/bin/python3
import numpy as np
from PIL import Image
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import datetime
from datetime import date, timedelta
from pathlib import Path
from glob import glob

#---------------------------------------------------------------------
# This python script parses a very specific instance of rtl_433 output
# it aggregates data of multiple files and server a webpage where this
# data is displayed as graphs
#---------------------------------------------------------------------



#-----------------------------------------------------------
# Code for filtering, interpolating and concatenate logfiles
#-----------------------------------------------------------
sensorOne=0.0
sensorTwo=0.0
sensorThree=0.0

allCSVFiles = glob("/home/rogier/Radio/Logs/FM*.csv")
allCSVFiles.sort()

outputFile = open('/home/rogier/Radio/Logs/AllData.csv','w')

outputFile.write("time,bresser_ch1,bresser_ch2,nexus\n")

for currentFile in allCSVFiles:
  if ("20230915" in currentFile):
    print("Skipping 20230915 on purpose. MUHAHAHAHAA! nah, it's silly data. We should really skip it.")
  else:
    with open(currentFile) as fp:
      for line in fp:
        if (";" in line):
          currentComponents = line.split(";")
        else:
          currentComponents = line.split(",")

        dirtyBit = 0
        if (currentComponents[3]=="Nexus-TH"):
          dirtyBit = 1
          sensorThree = float(currentComponents[8])

        if (currentComponents[3]=="Bresser-3CH"):
          if (currentComponents[6]=="1"):
            dirtyBit = 1
            sensorOne = float(currentComponents[13])
            sensorOne = (sensorOne-32)*(5/9)
          elif (currentComponents[6]=="2"):
            dirtyBit = 1
            sensorTwo = float(currentComponents[13])
            sensorTwo = (sensorTwo-32)*(5/9)

        if ((dirtyBit != 0) and (sensorOne != 0) and (sensorTwo != 0) and (sensorThree != 0)):
          outputFile.write(currentComponents[0]+","+str(sensorOne)+","+str(sensorTwo)+","+str(sensorThree)+'\n')

outputFile.flush()
outputFile.close()

#---------------------------------
# Code for generating the web page
#---------------------------------
sensorValues = pd.read_csv('/home/rogier/Radio/Logs/AllData.csv')

allFig = go.Figure()
correlationOneFig = px.scatter(x=sensorValues.bresser_ch1, y=sensorValues.nexus)
correlationTwoFig = px.scatter(x=sensorValues.bresser_ch2, y=sensorValues.nexus)

bresserOneFig = go.Figure()
bresserTwoFig = go.Figure()
nexusFig = go.Figure()
allFig.add_trace(go.Scatter(x=sensorValues.time, y=sensorValues.bresser_ch1, mode='lines', name='Sensor one'))
allFig.add_trace(go.Scatter(x=sensorValues.time, y=sensorValues.bresser_ch2, mode='lines', name='Sensor two'))
allFig.add_trace(go.Scatter(x=sensorValues.time, y=sensorValues.nexus, mode='lines', name='Weather station'))
bresserOneFig.add_trace(go.Scatter(x=sensorValues.time, y=sensorValues.bresser_ch1, mode='lines', name='Sensor one'))
bresserTwoFig.add_trace(go.Scatter(x=sensorValues.time, y=sensorValues.bresser_ch2, mode='lines', name='Sensor two'))
nexusFig.add_trace(go.Scatter(x=sensorValues.time, y=sensorValues.nexus, mode='lines', name='Weather station'))

app = dash.Dash(__name__)
app.title = 'Olaf dashboard'
app.layout = html.Div([
  dcc.Tabs([
    dcc.Tab(label='Alles', children=[
      html.H1("Alles", style={'text-align':'center'}),
      dcc.Graph(id="allSensors", figure=allFig),
      html.H1("Correlatie met sensor een", style={'text-align':'center'}),
      dcc.Graph(id="correlationA", figure=correlationOneFig),
      html.H1("Correlatie met sensor twee", style={'text-align':'center'}),
      dcc.Graph(id="correlationB", figure=correlationTwoFig)
    ]),
    dcc.Tab(label='Sensor een', children=[
      html.H1("Sensor een", style={'text-align':'center'}),
      dcc.Graph(id="sensorOne", figure=bresserOneFig)
    ]),
    dcc.Tab(label='Sensor twee', children=[
      html.H1("Sensor twee", style={'text-align':'center'}),
      dcc.Graph(id="sensorTwo", figure=bresserTwoFig),
    ]),
    dcc.Tab(label='Weerstation buurman', children=[
      html.H1("Weerstation buurman", style={'text-align':'center'}),
      dcc.Graph(id="sensorThree", figure=nexusFig)
    ]),
    dcc.Tab(label='Correlatie', children=[
      html.H1("Correlatie met sensor een", style={'text-align':'center'}),
      dcc.Graph(id="correlationOne", figure=correlationOneFig),
      html.H1("Correlatie met sensor twee", style={'text-align':'center'}),
      dcc.Graph(id="correlationTwo", figure=correlationTwoFig)
    ])
  ])
])

if __name__ == '__main__':
    app.run_server(debug=True,port=8765,host='0.0.0.0')

import pandas as pd
import numpy as np
import scipy as sp
import os as os
import csv
import psycopg2
import datetime
import mysql.connector
from array import *
import datetime as datetime

# Test Code simply defining curve classes

class curve:
    curveID=""
    curveName=""
    curveType=""
    compounding = ""
    classification1 = ""
    classification2 = ""
    classification3 = ""
    classification4 = ""


    class rates:
        AsOfDate = datetime.datetime.now();
        AsAtDate = datetime.datetime.now();
        rateDate=[]
        rateValue=[]
        modifiedRateDate=[]
        modifiedRateValue=[]

    class shockedRates:
        scenarioCurveID = []
        scenarioCurveName = []
        AsOfDate = [datetime.datetime.now()];
        AsAtDate = [datetime.datetime.now()];
        rateDate=[[],[]]
        rateValue=[[],[]]
        modifiedRateDate=[[],[]]
        modifiedRateValue=[[],[]]


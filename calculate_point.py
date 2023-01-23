#Importando bibliotecas
import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import pandas as pd


#Cálculo das propriedades termodinâmicas

def propriedades(ponto):
    variaveis=['T','P','HMASS','SMASS','Q']
    input_var=list(ponto.keys())
    output_var=[variable for variable in variaveis if variable not in input_var]
    outputs=PropsSI(output_var,input_var[0],ponto[input_var[0]],input_var[1],ponto[input_var[1]],ponto['refrigerant'])

    for index,variable in enumerate(output_var):
        ponto[variable]=outputs[index]

    return ponto




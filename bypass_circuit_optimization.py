import pandas as pd
import copy
import os
from bypass_circuit_cycle import calculate_bypass_circuit_cycle

####DADOS####

input_values = {
    't_internal_env_ht': 5 + 273.15,
    'approach_condenser': 5,
    't_internal_env_lt': -15 + 273.15,
    'approach_evaporator_lt': 5,
    'approach_evaporator_ht':20,
    'q_evaporator_ht': 75,
    'q_evaporator_lt': 75,
    'x_5':0,
    'x_8':0,
    'isentropic_efficiency': 0.7,
}

input_ranges = {
    'refrigerants': ['R22','R32','R134a','R290','R404a','R410a','R600','R600a', 'NH3','R1234yf', 'R1234ze(E)'],
    't_external': [20,25,30,35]
    }

def golden(input_values,x,y,lower_threshold,upper_threshold,tol,c):

    a=input_values[lower_threshold]
    b=input_values[upper_threshold]

    x1=a*c+(1-c)*b
    x2=(1-c)*a+b*c
    
    input_values_x = copy.copy(input_values)
    
    input_values_x[x]=x1
    cycle_1=calculate_bypass_circuit_cycle(input_values_x)
    f_x1=cycle_1[y]

    input_values_x[x]=x2
    cycle_2=calculate_bypass_circuit_cycle(input_values_x)
    f_x2=cycle_2[y] 
    
    while cycle_1['minimum_ad']<0:
        a=x1
        x1=a*c+(1-c)*b
        input_values_x[x]=x1
        cycle_1=calculate_bypass_circuit_cycle(input_values_x)
        f_x1=cycle_1[y]

        

    while cycle_2['minimum_ad']<0:
        b=x2
        x2=(1-c)*a+b*c
        input_values_x[x]=x2
        cycle_2=calculate_bypass_circuit_cycle(input_values_x)
        f_x2=cycle_2[y]

    if x2<a:
        x2=a*(1-c)+c*b

    if x1>b:
        x1=a*c+(1-c)*b

    delta_x=x2-x1
    
    while abs(delta_x)>tol:
        
        input_values_x = copy.copy(input_values)

        if f_x1<f_x2:
            a=x1
            x1=x2
            f_x1=f_x2
            x2=(1-c)*a+b*c

            input_values_x[x]=x2
            cycle_2=calculate_bypass_circuit_cycle(input_values_x)
            f_x2=cycle_2[y]

            while cycle_2['minimum_ad']<0:
                b=x2
                x2=(1-c)*a+b*c

                input_values_x[x]=x2
                cycle_2=calculate_bypass_circuit_cycle(input_values_x)
                f_x2=cycle_2[y]

            if x1>b:
                x1=a*c+(1-c)*b
                           
        else:
            b=x2
            x2=x1
            f_x2=f_x1

            x1=a*c+(1-c)*b

            input_values_x[x]=x1
            cycle_1=calculate_bypass_circuit_cycle(input_values_x)
            f_x1=cycle_1[y]

            while cycle_1['minimum_ad']<0:
                a=x1              
                x1=a*c+(1-c)*b

                input_values_x[x]=x1
                cycle_1=calculate_bypass_circuit_cycle(input_values_x)
                f_x1=cycle_1[y]

            if x2<a:
                x2=a*(1-c)+c*b

        delta_x=x2-x1

    xnew=(x2+x1)/2

    return xnew

def calculate_points_bypass_circuit_cycle(input_values, y,tol,c):
    current_cycle = calculate_bypass_circuit_cycle(input_values)

    x5=golden(input_values,'x_5',y,'lower_x5','upper_x5',tol,c)
    input_values['x_5'] = x5
    x8=golden(input_values,'x_8',y,'lower_x8','upper_x8',tol,c)
    input_values['x_8'] = x8

    next_cycle = calculate_bypass_circuit_cycle(input_values)

    
    return current_cycle, next_cycle

  
def optimize_bypass_circuit_cycle(input_values, y):
    c=0.97
    tol=10**(-5)

    input_values_x = copy.copy(input_values)
    cycle=calculate_bypass_circuit_cycle(input_values_x)

    input_values['lower_x5']=0
    input_values['lower_x8']=0


    input_values['upper_x5']=cycle['x5_max']
    input_values['upper_x8']=cycle['x8_max']
    input_values['x_5']=cycle['x5_max']/2
    input_values['x_8']=cycle['x8_max']/2

    
    error = 1
    while abs(error) >= 10**(-8):
        current_cycle, next_cycle = calculate_points_bypass_circuit_cycle(input_values, y,tol,c)
        error = (next_cycle[y] - current_cycle[y])/next_cycle[y]

    
    optimized_cycle = calculate_bypass_circuit_cycle(input_values)

        
    return optimized_cycle

def optimize_bypass_circuit_cycle_with_multiple_refrigerants(input_values, y ,input_ranges):
    original_input_values = copy.copy(input_values)
    results = pd.DataFrame(columns=[
        'Refrigerante',
        'Temperatura ambiente',
        'Trabalho do compressor',
        'Carga Frigorífica Geladeira',
        'Carga Frigorífica Freezer',
        'COP',
        'Eficiência Exergética',
        'Resfriamento FFC',
        'Resfriamento FZC',
        'f',
        'x5',
        'x8',
])
    n = 0
    print('Starting')
    for refrigerant in input_ranges['refrigerants']:
        for t_external in input_ranges['t_external']:
            n += 1
            input_values = copy.copy(original_input_values)
            input_values['refrigerant'] = refrigerant
            input_values['t_external'] = t_external + 273.15
            optimized_cycle= optimize_bypass_circuit_cycle(input_values, y)
            print(str(n * 100 / (len(input_ranges['refrigerants']) * len(input_ranges['t_external']))) + '%')
            results = results.append({
                'Refrigerante': refrigerant,
                'Temperatura ambiente': t_external,
                'Trabalho do compressor': optimized_cycle['work'],
                'Carga Frigorífica Geladeira': optimized_cycle['q_evaporator_ht'],
                'Carga Frigorífica Freezer': optimized_cycle['q_evaporator_lt'],
                'COP': optimized_cycle['cop'],
                'Resfriamento FFC':optimized_cycle['cooling_FFC'],
                'Resfriamento FZC':optimized_cycle['cooling_FZC'],
                'f':optimized_cycle['f'],
                'x5':optimized_cycle['x5'],
                'x8':optimized_cycle['x8'],
                'Eficiência Exergética': optimized_cycle['exergy_efficiency_components'],
            }, ignore_index=True)

            


    print('Done')
    return results



optimized_exergy_efficiency_table = optimize_bypass_circuit_cycle_with_multiple_refrigerants(input_values, 'cop', input_ranges)

# Create a Pandas Excel writer using XlsxWriter as the engine
writer = pd.ExcelWriter('bypass_cycle_optimization.xlsx', engine='xlsxwriter')

# Close the Pandas Excel writer and output the Excel file
optimized_exergy_efficiency_table.to_excel(writer, sheet_name='Sheet1')

# Convert the dataframe to an XlsxWriter Excel object
writer.close()

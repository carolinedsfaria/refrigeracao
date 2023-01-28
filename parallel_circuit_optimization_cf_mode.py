import pandas as pd
import copy
import os
from parallel_circuit_cycle_cf_mode import calculate_parallel_circuit_cycle


##################################################DATA##########################################################

input_values = {
    'approach_condenser': 5,
    't_internal_env_lt': -15 + 273.15,
    'approach_evaporator_lt': 5,
    'q_evaporator': 75,
    'hx_efficiency':0.5,
    'isentropic_efficiency': 0.7,
}

input_ranges = {
    'refrigerants': ['R22','R32','R134a','R290','R404a','R410a','R600','R600a', 'NH3','R1234yf', 'R1234ze(E)'],
    't_external': [20,25,30,35]
    }

################################################################################################################

def golden(input_values,x,y,lower_threshold,upper_threshold,tol,c):

    a=input_values[lower_threshold]
    b=input_values[upper_threshold]


    x1=a*c+(1-c)*b
    x2=(1-c)*a+b*c
    
    input_values_x = copy.copy(input_values)
    
    input_values_x[x]=x1
    cycle_1=calculate_parallel_circuit_cycle(input_values_x)
    f_x1=cycle_1[y]

    input_values_x[x]=x2
    cycle_2=calculate_parallel_circuit_cycle(input_values_x)
    f_x2=cycle_2[y] 
       


    delta_x=x2-x1
    
    while abs(delta_x)>tol:
        
        input_values_x = copy.copy(input_values)

        if f_x1<f_x2:
            a=x1
            x1=x2
            f_x1=f_x2
            x2=(1-c)*a+b*c

            input_values_x[x]=x2
            cycle_2=calculate_parallel_circuit_cycle(input_values_x)
            f_x2=cycle_2[y]

            
                           
        else:
            b=x2
            x2=x1
            f_x2=f_x1

            x1=a*c+(1-c)*b

            input_values_x[x]=x1
            cycle_1=calculate_parallel_circuit_cycle(input_values_x)
            f_x1=cycle_1[y]

            

        delta_x=x2-x1

    xnew=(x2+x1)/2

    return xnew

def calculate_points_parallel_circuit_cycle(input_values, y,tol,c):
    current_cycle = calculate_parallel_circuit_cycle(input_values)
    input_values['upper_ef'] = current_cycle['upper_ef']
    input_values['lower_ef'] = 0.5
    hx_efficiency=golden(input_values,'hx_efficiency',y,'lower_ef','upper_ef',tol,c)
    input_values['hx_efficiency'] = hx_efficiency

    next_cycle = calculate_parallel_circuit_cycle(input_values)

    
    return current_cycle, next_cycle

  
def optimize_parallel_circuit_cycle(input_values, y):
    c=0.97
    tol=10**(-5)
    
    error = 1
    while abs(error) >= 10**(-8):
        current_cycle, next_cycle = calculate_points_parallel_circuit_cycle(input_values, y,tol,c)
        error = (next_cycle[y] - current_cycle[y])/next_cycle[y]

    
    optimized_cycle = calculate_parallel_circuit_cycle(input_values)

        
    return optimized_cycle

def optimize_parallel_circuit_cycle_with_multiple_refrigerants(input_values, y ,input_ranges):
    original_input_values = copy.copy(input_values)
    results = pd.DataFrame(columns=[
        'Refrigerante',
        'Temperatura ambiente',
        'Trabalho do compressor',
        'Carga Frigorífica',
        'COP',
        'Eficiência Exergética',
        'Eficiência do trocador',
        'Grau de subresfriamento',

])
    n = 0
    print('Starting')
    for refrigerant in input_ranges['refrigerants']:
        for t_external in input_ranges['t_external']:
            n += 1
            input_values = copy.copy(original_input_values)
            input_values['refrigerant'] = refrigerant
            input_values['t_external'] = t_external + 273.15
            optimized_cycle= optimize_parallel_circuit_cycle(input_values, y)
            print(str(n * 100 / (len(input_ranges['refrigerants']) * len(input_ranges['t_external']))) + '%')
            results = results.append({
                'Refrigerante': refrigerant,
                'Temperatura ambiente': t_external,
                'Trabalho do compressor': optimized_cycle['work'],
                'Carga Frigorífica': optimized_cycle['q_evaporator'],
                'COP': optimized_cycle['cop'],
                'Grau de subresfriamento':optimized_cycle['cooling_FZC'],
                'Eficiência Exergética': optimized_cycle['exergy_efficiency_components'],
                'Eficiência do trocador':optimized_cycle['Eficiência do trocador'],
            }, ignore_index=True)

            


    print('Done')
    return results



optimized_table = optimize_parallel_circuit_cycle_with_multiple_refrigerants(input_values, 'cop', input_ranges)

# Create a Pandas Excel writer using XlsxWriter as the engine
writer = pd.ExcelWriter('parallel_cycle_optimization_cf_mode.xlsx', engine='xlsxwriter')

# Close the Pandas Excel writer and output the Excel file
optimized_table.to_excel(writer, sheet_name='Sheet1')

# Convert the dataframe to an XlsxWriter Excel object
writer.close()

import pandas as pd
import copy
import os
from expander_cycle import calculate_expander_cycle

####DADOS####

input_values_geladeira = {
    't_internal_env': 5 + 273.15,
    'approach_condenser': 5,
    'approach_evaporator': 5,
    'approach_evaporator_lt': 5,
    'q_evaporator': 75,
    'q_evaporator_lt': 75,
    'subcooling':0,
    'compressor_isentropic_efficiency': 0.7,
    'expander_isentropic_efficiency': 0.43,
}

input_values_freezer = {
    't_internal_env': -15 + 273.15,
    'approach_condenser': 5,
    'approach_evaporator': 5,
    'approach_evaporator_lt': 5,
    'q_evaporator': 75,
    'q_evaporator_lt': 75,
    'subcooling':0,
    'compressor_isentropic_efficiency': 0.7,
    'expander_isentropic_efficiency': 0.43,
}



input_ranges = {
    'refrigerants': ['NH3','R22','R32','R134a','R290','R404a','R410a','R600','R600a', 'R1234yf', 'R1234ze(E)'],
    't_external': [20,25,30,35]
    }



def golden(input_values,x,y,lower_threshold,upper_threshold,tol,c):

    a=input_values[lower_threshold]
    b=input_values[upper_threshold]

    x1=a*c+(1-c)*b
    x2=(1-c)*a+b*c
    
    input_values_x = copy.copy(input_values)
    
    input_values_x[x]=x1
    cycle_1=calculate_expander_cycle(input_values_x)
    f_x1=cycle_1[y]

    input_values_x[x]=x2
    cycle_2=calculate_expander_cycle(input_values_x)
    f_x2=cycle_2[y]

    while cycle_1['minimum_ad']<0:
        a=x1
        x1=a*c+(1-c)*b
        input_values_x[x]=x1
        cycle_1=calculate_expander_cycle(input_values_x)
        f_x1=cycle_1[y]

        

    while cycle_2['minimum_ad']<0:
        b=x2
        x2=(1-c)*a+b*c
        input_values_x[x]=x2
        cycle_2=calculate_expander_cycle(input_values_x)
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
            cycle_2=calculate_expander_cycle(input_values_x)
            f_x2=cycle_2[y]
            

            while cycle_2['minimum_ad']<0:
                b=x2
                x2=(1-c)*a+b*c

                input_values_x[x]=x2
                cycle_2=calculate_expander_cycle(input_values_x)
                f_x2=cycle_2[y]

            
            if x1>b:
                x1=a*c+(1-c)*b
           
        else:
            b=x2
            x2=x1
            f_x2=f_x1
            x1=a*c+(1-c)*b

            input_values_x[x]=x1
            cycle_1=calculate_expander_cycle(input_values_x)
            f_x1=cycle_1[y]

            
            while cycle_1['minimum_ad']<0:
                a=x1
                x1=a*c+(1-c)*b

                input_values_x[x]=x1
                cycle_1=calculate_expander_cycle(input_values_x)
                f_x1=cycle_1[y]

            if x2<a:
                x2=a*(1-c)+c*b
                
            

        delta_x=x2-x1

    
       
    xnew=(x2+x1)/2


    return xnew

def calculate_points_expander_cycle(input_values, y,tol,c):
    current_cycle = calculate_expander_cycle(input_values)
       
    x=golden(input_values,'subcooling',y,'lower_cooling','upper_cooling',tol,c)
  
    input_values['subcooling'] = x

    next_cycle = calculate_expander_cycle(input_values)

    
    return current_cycle, next_cycle

def optimize_expander_cycle(input_values, y):
    c=0.97
    tol=10**(-8)

    input_values_x = copy.copy(input_values)
    cycle=calculate_expander_cycle(input_values_x)
    subcooling_max = input_values['subcooling']


    vapor_quote=cycle['x5']
    while vapor_quote>10**(-5):            
        subcooling_max=subcooling_max + 0.01

        input_values_x['subcooling'] = subcooling_max
        cycle = calculate_expander_cycle(input_values_x)
        vapor_quote=cycle['x5']

    input_values['lower_cooling']=0
    input_values['upper_cooling']=subcooling_max


    error = 1
    while  abs(error) >= 10**(-8):
        current_cycle, next_cycle = calculate_points_expander_cycle(input_values, y,tol,c)
        error = (next_cycle[y] - current_cycle[y])/next_cycle[y]
    optimized_cycle = calculate_expander_cycle(input_values)
        
    return optimized_cycle

def optimize_expander_cycle_with_multiple_refrigerants(input_values, y ,input_ranges):
    original_input_values = copy.copy(input_values)
    results = pd.DataFrame(columns=[
        'Refrigerante',
        'Temperatura ambiente',
        'Trabalho do compressor',
        'Carga Frigorífica',
        'COP',
        'Eficiência Exergética',
        'Resfriamento no trocador'])
    n = 0
    print('Starting')
    for refrigerant in input_ranges['refrigerants']:
        print(refrigerant)
        for t_external in input_ranges['t_external']:
            print(t_external)
            n += 1
            input_values = copy.copy(original_input_values)
            input_values['refrigerant'] = refrigerant
            input_values['t_external'] = t_external + 273.15
            optimized_cycle = optimize_expander_cycle(input_values, y)
            print(str(n * 100 / (len(input_ranges['refrigerants']) * len(input_ranges['t_external']))) + '%')
            results = results.append({
                'Refrigerante': refrigerant,
                'Temperatura ambiente': t_external,
                'Trabalho do compressor': optimized_cycle['work'],
                'Carga Frigorífica': optimized_cycle['q_evaporator'],
                'COP': optimized_cycle['cop'],
                'Resfriamento no trocador':optimized_cycle['cooling'],
                'Eficiência Exergética': optimized_cycle['exergy_efficiency_components'],
            }, ignore_index=True)
            


    print('Done')
    return results



optimized_cop_table_geladeira = optimize_expander_cycle_with_multiple_refrigerants(input_values_geladeira, 'cop', input_ranges)
optimized_cop_table_freezer = optimize_expander_cycle_with_multiple_refrigerants(input_values_freezer, 'cop', input_ranges)



##GELADEIRA

# Create a Pandas Excel writer using XlsxWriter as the engine
writer = pd.ExcelWriter('expander_cycle_geladeira.xlsx', engine='xlsxwriter')

# Close the Pandas Excel writer and output the Excel file
optimized_cop_table_geladeira.to_excel(writer, sheet_name='Sheet1')

# Convert the dataframe to an XlsxWriter Excel object
writer.close()


##FREEZER

# Create a Pandas Excel writer using XlsxWriter as the engine
writer = pd.ExcelWriter('expander_cycle_freezer.xlsx', engine='xlsxwriter')

# Close the Pandas Excel writer and output the Excel file
optimized_cop_table_freezer.to_excel(writer, sheet_name='Sheet1')

# Convert the dataframe to an XlsxWriter Excel object
writer.close()

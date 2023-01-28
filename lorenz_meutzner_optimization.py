from CoolProp.CoolProp import PropsSI
import pandas as pd
import copy

from lorenz_meutzner_cycle import calculate_lorenz_meutzner_cycle

##################################################DATA##########################################################


input_values = {
    't_internal_env_lt': -15 + 273.15,
    't_internal_env_ht': 5 + 273.15,
    'approach_condenser': 5,
    'approach_evaporator_lt': 0,
    'q_evaporator_ht': 75,
    'q_evaporator_lt': 75,
    'isentropic_efficiency': 0.7,
    'hx_efficiency':0.5,
    
}

input_ranges = {'refrigerants': ['HEOS::R290[0.467691317]&R600[0.532308683]','HEOS::R290[0.467691317]&R600a[0.532308683]','HEOS::R22[0.5]&R142b[0.5]'],
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
    cycle_1=calculate_lorenz_meutzner_cycle(input_values_x)
    f_x1=cycle_1[y]

    input_values_x[x]=x2
    cycle_2=calculate_lorenz_meutzner_cycle(input_values_x)
    f_x2=cycle_2[y]
    
    delta_x=x2-x1
    
    while abs(delta_x)<tol:
        
        input_values_x = copy.copy(input_values)

        if f_x1<f_x2:
            a=x1
            input_values[lower_threshold]=a

            x1=x2

            f_x1=f_x2

            x2=(1-c)*a+b*c

            input_values_x[x]=x2
            f_x2=calculate_lorenz_meutzner_cycle(input_values_x)[y]

        else:
            b=x2
            input_values[upper_threshold]=b

            x2=x1

            f_x2=f_x1

            x1=a*c+(1-c)*b

            input_values_x[x]=x1
            f_x1=calculate_lorenz_meutzner_cycle(input_values_x)[y]

        delta_x=x2-x1

    xnew=(x2+x1)/2

    return xnew

def calculate_points_lorenz_meutzner_cycle(input_values, y,tol,c):
    current_cycle = calculate_lorenz_meutzner_cycle(input_values)
    input_values['lower_efficiency'] = 0.5
    input_values['upper_efficiency'] = current_cycle['upper_efficiency']
    
    hx_efficiency=golden(input_values,'hx_efficiency',y,'lower_efficiency','upper_efficiency',tol,c)
    input_values['hx_efficiency'] = hx_efficiency
    
    next_cycle = calculate_lorenz_meutzner_cycle(input_values)

    
    return current_cycle, next_cycle

  
def optimize_lorenz_meutzner_cycle(input_values, y):

    c=0.97
    tol=10**(-5)
    
    error = 1
    while abs(error) >= 10**(-8):
        current_cycle, next_cycle = calculate_points_lorenz_meutzner_cycle(input_values, y,tol,c)
        error = (next_cycle[y] - current_cycle[y])/next_cycle[y]
    optimized_cycle = calculate_lorenz_meutzner_cycle(input_values)
        
    return optimized_cycle

def optimize_lorenz_meutzner_cycle_with_multiple_refrigerants(input_values, y ,input_ranges):
    original_input_values = copy.copy(input_values)
    results = pd.DataFrame(columns=[
        'Refrigerante',
        'Temperatura ambiente',
        'Trabalho do compressor',
        'Carga frigorífica EAT',
        'Carga frigorífica EBT',
        'COP',
        'Eficiência exergética',
        'Eficiência do trocador']
    )
    n = 0
    print('Starting')
    for refrigerant in input_ranges['refrigerants']:
        for t_external in input_ranges['t_external']:
            n += 1
            input_values = copy.copy(original_input_values)
            input_values['refrigerant'] = refrigerant
            input_values['t_external'] = t_external + 273.15
            optimized_cycle = optimize_lorenz_meutzner_cycle(input_values, y)
            print(str(n * 100 / (len(input_ranges['refrigerants']) * len(input_ranges['t_external']))) + '%')
           

            results = results.append({
                'Refrigerante': refrigerant,
                'Temperatura ambiente': t_external,
                'Trabalho do compressor': optimized_cycle['work'],
                'Carga frigorífica EAT': optimized_cycle['q_evaporator_ht'],
                'Carga frigorífica EBT': optimized_cycle['q_evaporator_lt'],
                'COP': optimized_cycle['cop'],
                'Eficiência do trocador':optimized_cycle['hx_efficiency'],
                'Eficiência exergética': optimized_cycle['exergy_efficiency_components'],
            }, ignore_index=True)


    print('Done')
    return results




optimized_table = optimize_lorenz_meutzner_cycle_with_multiple_refrigerants(input_values, 'cop', input_ranges)

# Create a Pandas Excel writer using XlsxWriter as the engine
writer = pd.ExcelWriter('lorenz_meutzner_optimized.xlsx', engine='xlsxwriter')

# Close the Pandas Excel writer and output the Excel file
optimized_table.to_excel(writer, sheet_name='Sheet1')

# Convert the dataframe to an XlsxWriter Excel object
writer.close()

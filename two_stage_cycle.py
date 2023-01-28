#Two-stage cycle

from CoolProp.CoolProp import PropsSI
import pandas as pd
import copy

from calculate_point import propriedades


##################################################DATA##########################################################


input_values = {
    't_internal_env_ht': 5 + 273.15,
    'approach_condenser': 5,
    't_internal_env_lt': -15 + 273.15,
    'approach_evaporator_ht': 5,
    'approach_evaporator_lt': 5,
    'q_evaporator_ht': 75,
    'q_evaporator_lt': 75,
    'isentropic_efficiency': 0.7,
}

input_ranges = {
    'refrigerants': ['R22','R32','R134a','R290','R404a','R410a','R600','R600a', 'NH3','R1234yf', 'R1234ze(E)'],
    't_external': [20,25,30,35]
    }

################################################################################################################



# Calculates two stage cycle 
def calculate_two_stage_cycle(cycle_inputs):

    # Point 3 (after condenser)

    ## Identificar mistura zeotrópica
    
    point_3l = {'Q': 0,
                'T': cycle_inputs['t_external'] + cycle_inputs['approach_condenser'],
                'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_3l)

    point_3v = {'Q': 1,
                'T': cycle_inputs['t_external'] + cycle_inputs['approach_condenser'],
                'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_3v)

    if (point_3l['P']-point_3v['P'])>0:

        point_3= {'Q': 0,
                  'P': point_3v['P'],
                  'refrigerant': cycle_inputs['refrigerant']
                       }
        propriedades(point_3)

        
    else:

        point_3=point_3l
    
    
    # Point 4 (after expansion device HTE)


    ## Identificar mistura zeotrópica
    t4=cycle_inputs['t_internal_env_ht'] - cycle_inputs['approach_evaporator_ht']
    h4=point_3['HMASS']
        
    sat_liq={'Q': 0,
             'T': t4,
             'refrigerant': cycle_inputs['refrigerant']}
    propriedades(sat_liq)
    hl_sat=sat_liq['HMASS']
    Pl_sat=sat_liq['P']

    sat_vap = {'Q': 1,
               'T': t4,
               'refrigerant': cycle_inputs['refrigerant']}
    propriedades(sat_vap)
    hv_sat=sat_vap['HMASS']
    Pv_sat=sat_vap['P']


    if (Pl_sat-Pv_sat)>0: #mistura zeotrópica

        x4=(h4-hl_sat)/(hv_sat-hl_sat)
        P4=Pv_sat*x4+(1-x4)*Pl_sat

        point = {'HMASS':h4,
                 'P': P4,
                 'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point)
        erro=t4-point['T']

        while abs(erro)>=10**(-3):
            P_4=point['P']+erro/10**(5)
            point = {'HMASS':h4,
                     'P': P_4,
                     'refrigerant': cycle_inputs['refrigerant']}
            propriedades(point)
            erro=t4-point['T']

        point_4 = {'HMASS':h4,
                   'P': point['P'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_4)

        # Point 1 (before second compressor)  
        point_1 = {'Q': 1,
                   'P': point_4['P'],
                   'refrigerant': cycle_inputs['refrigerant']
                       }
        propriedades(point_1)
        

    else: #não zeotrópico

        # Point 1 (before second compressor)  
        point_1 = {'Q': 1,
                   'T': t4,
                   'refrigerant': cycle_inputs['refrigerant']
                       }
        propriedades(point_1)

        point_4 = {'HMASS': point_3['HMASS'],
                   'P': point_1['P'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_4)


    #Point 6 (before expansion device LTE)
    point_6 = {'Q': 0,
               'T': cycle_inputs['t_internal_env_ht'] - cycle_inputs['approach_evaporator_ht'],
               'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_6)




    ###Freezer###

    ## Identificar mistura zeotrópica
    t7=cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt']
    h7=point_6['HMASS']
        
    sat_liq={'Q': 0,
             'T': t7,
             'refrigerant': cycle_inputs['refrigerant']}
    propriedades(sat_liq)
    hl_sat=sat_liq['HMASS']
    Pl_sat=sat_liq['P']

    sat_vap = {'Q': 1,
               'T': t7,
               'refrigerant': cycle_inputs['refrigerant']}
    propriedades(sat_vap)
    hv_sat=sat_vap['HMASS']
    Pv_sat=sat_vap['P']

    if (Pl_sat-Pv_sat)>0: #mistura zeotrópica

        x7=(h7-hl_sat)/(hv_sat-hl_sat)
        P7=Pv_sat*x7+(1-x7)*Pl_sat

        point = {'HMASS':h7,
                 'P': P7,
                 'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point)
        erro=t7-point['T']

        while abs(erro)>=10**(-3):
            P_7=point['P']+erro/10**(5)
            point = {'HMASS':h7,
                     'P': P_7,
                     'refrigerant': cycle_inputs['refrigerant']}
            propriedades(point)
            erro=t7-point['T']

        point_7 = {'HMASS':h7,
                   'P': point['P'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_7)

        # Point 8 (after low temperature evaporator)  
        point_8 = {'Q': 1,
                   'P': point_7['P'],
                   'refrigerant': cycle_inputs['refrigerant']
                       }
        propriedades(point_8)

    else: #não zeotrópico

        # Point 8 (after low temperature evaporator)  
        point_8 = {'Q': 1,
                   'T': cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt'],
                   'refrigerant': cycle_inputs['refrigerant']
                       }
        propriedades(point_8)
        
        point_7 = {'HMASS': point_6['HMASS'],
                   'P': point_8['P'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_7)

    #Point 9 (after first compressor)
    
    point_9_isen = {'SMASS': point_8['SMASS'], 
                    'P': point_4['P'],
                    'refrigerant': cycle_inputs['refrigerant']
                   }
    propriedades(point_9_isen)

    point_9 = {'P': point_4['P'], 
               'HMASS': point_8['HMASS'] + (point_9_isen['HMASS'] - point_8['HMASS']) / cycle_inputs['isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_9)

    #Point 5
    q_evaporator_lt = cycle_inputs['q_evaporator_lt']
    q_evaporator_ht = cycle_inputs['q_evaporator_ht']  
    m_lt=q_evaporator_lt / (point_8['HMASS'] - point_7['HMASS'])
    
    f=m_lt*(point_1['HMASS']-point_4['HMASS'])/(q_evaporator_ht-m_lt*(point_6['HMASS']-point_9['HMASS']))

    point_5 = {'P': point_4['P'],
               'HMASS': f*(point_6['HMASS']-point_9['HMASS'])+point_1['HMASS'],
               'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_5)

    #Point 2 (after second compressor)
    
    point_2_isen = {'SMASS': point_1['SMASS'], 
                    'P': point_3['P'],
                    'refrigerant': cycle_inputs['refrigerant']
                   }
    propriedades(point_2_isen)

    point_2 = {'P': point_3['P'], 
               'HMASS': point_1['HMASS'] + (point_2_isen['HMASS'] - point_1['HMASS']) / cycle_inputs['isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_2)


    
    m_ht=q_evaporator_ht / (point_5['HMASS'] - point_4['HMASS'])

    work_1st_comp = m_lt* (point_9['HMASS'] - point_8['HMASS'])
    work_2nd_comp = m_ht * (point_2['HMASS'] - point_1['HMASS'])
        
    q_evap=q_evaporator_lt+q_evaporator_ht
    work=work_1st_comp+work_2nd_comp

  
    # COP    
    cop = (q_evap)/work
    
    # COP Carnot
    cop_carnot_ht = cycle_inputs['t_internal_env_ht'] / (cycle_inputs['t_external'] - cycle_inputs['t_internal_env_ht'])
    cop_carnot_lt = cycle_inputs['t_internal_env_lt'] / (cycle_inputs['t_external'] - cycle_inputs['t_internal_env_lt'])
    
    w_carnot_ht = q_evaporator_ht / cop_carnot_ht
    w_carnot_lt = q_evaporator_lt / cop_carnot_lt
    
    cop_carnot = (q_evaporator_ht + q_evaporator_lt) / (w_carnot_ht + w_carnot_lt)

    # Exergy Destruction Components
    t_0 = cycle_inputs['t_external']
    
    first_compressor_exergy_destruction = m_lt * t_0 * (point_9['SMASS'] - point_8['SMASS'])
    second_compressor_exergy_destruction = m_ht * t_0 * (point_2['SMASS'] - point_1['SMASS'])
    compressor_exergy_destruction=first_compressor_exergy_destruction+second_compressor_exergy_destruction
    
    condenser_exergy_destruction = m_ht * t_0 * (point_3['SMASS'] - point_2['SMASS'] + (point_2['HMASS'] - point_3['HMASS']) / t_0)

    expansion_valve_ht_exergy_destruction = m_ht * t_0 * (point_4['SMASS'] - point_3['SMASS'])

    evaporator_ht_exergy_destruction = m_ht * t_0 * (point_5['SMASS'] - point_4['SMASS'] - (point_5['HMASS'] - point_4['HMASS']) / cycle_inputs['t_internal_env_ht'])

    separator_exergy_destruction = m_ht * t_0 * (point_1['SMASS'] - point_5['SMASS'])+m_ht *(point_5['HMASS']-point_1['HMASS'])+m_lt * t_0 * (point_6['SMASS'] - point_9['SMASS'])+m_lt *(point_9['HMASS']-point_6['HMASS'])

    expansion_valve_lt_exergy_destruction = m_lt * t_0 * (point_7['SMASS'] - point_6['SMASS'])

    evaporator_lt_exergy_destruction = m_lt * t_0 * (point_8['SMASS'] - point_7['SMASS'] - (point_8['HMASS'] - point_7['HMASS']) / cycle_inputs['t_internal_env_lt'])
    
    total_exergy_destruction = compressor_exergy_destruction + condenser_exergy_destruction + expansion_valve_ht_exergy_destruction + \
        evaporator_ht_exergy_destruction + separator_exergy_destruction + \
        expansion_valve_lt_exergy_destruction + evaporator_lt_exergy_destruction

    return {
        'work_1st_comp':work_1st_comp,
        'work_2nd_comp':work_2nd_comp,
        'm_ht': m_ht,
        'm_lt': m_lt,
        'f':f,
        'q_evaporator_ht': q_evaporator_ht,
        'q_evaporator_lt': q_evaporator_lt,
        'work': work,
        'cop': cop,
        'exergy_efficiency': cop / cop_carnot,
        'exergy_efficiency_components': 1 - total_exergy_destruction / work
        
    }


def generate_two_stage_cycle_table(input_values,input_ranges):
    original_input_values = copy.copy(input_values)
    results = pd.DataFrame(columns=[
        'Refrigerante',
        'Temperatura ambiente',
        'Trabalho dos compressores',
        'Carga Frigorífica Geladeira',
        'Carga Frigorífica Freezer',
        'f',
        'COP',
        'Eficiência Exergética']
    )
    n = 0
    print('Starting')
    for refrigerant in input_ranges['refrigerants']:
        for t_external in input_ranges['t_external']:
            n += 1
            input_values = copy.copy(original_input_values)
            input_values['refrigerant'] = refrigerant
            input_values['t_external'] = t_external + 273.15
            optimized_cycle = calculate_two_stage_cycle(input_values)
            print(str(n * 100 / (len(input_ranges['refrigerants']) * len(input_ranges['t_external']))) + '%')
            results = results.append({
                'Refrigerante': refrigerant,
                'Temperatura ambiente': t_external,
                'Trabalho dos compressores': optimized_cycle['work'],
                'Carga Frigorífica Geladeira': optimized_cycle['q_evaporator_ht'],
                'Carga Frigorífica Freezer': optimized_cycle['q_evaporator_lt'],
                'COP': optimized_cycle['cop'],
                'Eficiência Exergética': optimized_cycle['exergy_efficiency_components']}, ignore_index=True)
                      


    print('Done')
    return results



two_stage_table = generate_two_stage_cycle_table(input_values, input_ranges)

# Create a Pandas Excel writer using XlsxWriter as the engine
writer = pd.ExcelWriter('two_stage_cycle.xlsx', engine='xlsxwriter')

# Close the Pandas Excel writer and output the Excel file
two_stage_table.to_excel(writer, sheet_name='Sheet1')

# Convert the dataframe to an XlsxWriter Excel object
writer.close()
  

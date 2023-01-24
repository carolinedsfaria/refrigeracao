#Expander cycle with SLHX

#Importando bibliotecas
from CoolProp.CoolProp import PropsSI
import pandas as pd

from calculate_point import propriedades


# Calculates expander cycle (q_evaporators or work as inputs)
def calculate_expander_cycle(cycle_inputs):

    # Point 3 (after condenser)
    ## Identificar mistura azeotrópica
    
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

    if abs(point_3l['P']-point_3v['P'])>0:

        point_3= {'Q': 0,
                  'P': point_3v['P'],
                  'refrigerant': cycle_inputs['refrigerant']
                       }
        propriedades(point_3)
        
    else:

        point_3=point_3l

    # Point 4 (before expander)

    if cycle_inputs['subcooling'] > 10**(-1):
        point_4 = {'P': point_3['P'], 
                   'T': point_3['T'] - cycle_inputs['subcooling'],
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        propriedades(point_4)
    else:
        cycle_inputs['subcooling'] = 0
        point_4 = point_3

    
    # Point 6 (after evaporator)
    point_6 = {'Q': 1,
               'T': cycle_inputs['t_internal_env'] - cycle_inputs['approach_evaporator'],
               'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_6)

    # Point 5 (after expander)

    point_5_isen = {'SMASS': point_4['SMASS'],
                    'P': point_6['P'],
                    'refrigerant': cycle_inputs['refrigerant']}
    propriedades(point_5_isen)

    point_5 = {'P': point_6['P'],
               'HMASS': point_4['HMASS'] + (point_5_isen['HMASS'] - point_4['HMASS']) *cycle_inputs['expander_isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']}
    propriedades(point_5)


    # Point 1 (before compressor)

    point_1 = {'P': point_6['P'],
               'HMASS': point_3['HMASS']+point_6['HMASS']-point_4['HMASS'],
               'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_1)

    # Point 2 (after compressor)

    point_2_isen = {'SMASS': point_1['SMASS'],
                    'P': point_3['P'],
                    'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_2_isen)
    
    point_2 = {'P': point_3['P'],
               'HMASS': point_1['HMASS'] + (point_2_isen['HMASS'] - point_1['HMASS']) / cycle_inputs['compressor_isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_2)


    q_evaporator = cycle_inputs['q_evaporator']
        
    m = q_evaporator / (point_6['HMASS'] - point_5['HMASS'])

    work_compressor = m * (point_2['HMASS'] - point_1['HMASS'])
    work_expander = m * (point_4['HMASS'] - point_5['HMASS'])
        
    work=work_compressor -work_expander


  
    # COP    
    cop = (q_evaporator)/work
    
    # COP Carnot
    cop_carnot = cycle_inputs['t_internal_env'] / (cycle_inputs['t_external'] - cycle_inputs['t_internal_env'])


    # Exergy Destruction Components
    t_0 = cycle_inputs['t_external']
    
    compressor_exergy_destruction = m * t_0 * (point_2['SMASS'] - point_1['SMASS'])
    
    condenser_exergy_destruction = m * t_0 * (point_3['SMASS'] - point_2['SMASS'] + (point_2['HMASS'] - point_3['HMASS']) / cycle_inputs['t_external'])

    slhx_exergy_destruction = m * t_0 * (point_4['SMASS'] - point_3['SMASS']+point_1['SMASS'] - point_6['SMASS'])+ m *((point_3['HMASS'] - point_4['HMASS'])-(point_1['HMASS'] - point_6['HMASS']))

    expander_exergy_destruction = m * t_0 * (point_5['SMASS'] - point_4['SMASS'])

    evaporator_exergy_destruction = m * t_0 * (point_6['SMASS'] - point_5['SMASS'] - (point_6['HMASS'] - point_5['HMASS']) / cycle_inputs['t_internal_env'])
    
    total_exergy_destruction = compressor_exergy_destruction + condenser_exergy_destruction + slhx_exergy_destruction + \
        evaporator_exergy_destruction + expander_exergy_destruction

    minimum_ad=min(compressor_exergy_destruction,condenser_exergy_destruction,slhx_exergy_destruction,expander_exergy_destruction,evaporator_exergy_destruction)
    
    return {
        'm': m,
        'cooling':cycle_inputs['subcooling'],
        'minimum_ad':minimum_ad,
        'q_evaporator': q_evaporator,
        'work': work,
        'cop': cop,
        'subcooling':point_3['T']-point_4['T'],
        'exergy_efficiency': cop / cop_carnot,
        'exergy_efficiency_components': 1 - total_exergy_destruction / work,
                
    }

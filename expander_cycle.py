#Expander cycle with SLHX

#Importando bibliotecas
from CoolProp.CoolProp import PropsSI
import pandas as pd

from calculate_point import propriedades


def calculate_expander_cycle(cycle_inputs):

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


    # Point 6 
    point_6 = {'Q': 1,
               'T': cycle_inputs['t_internal_env'] - cycle_inputs['approach_evaporator'],
               'refrigerant': cycle_inputs['refrigerant']}
    propriedades(point_6)
    

    ######Calculate qmax########

    cp_min_ffc=min(point_3['C'],point_6['C'])
    qmax_ffc=cp_min_ffc*(point_3['T']-point_6['T'])
    e_hx=cycle_inputs['hx_efficiency']

    
    #Point 4
    

    point_4 = {'P': point_3['P'],
               'T': point_3['T'] - (e_hx*qmax_ffc)/point_3['C'],
               'refrigerant': cycle_inputs['refrigerant']
                  }
    propriedades(point_4)

            
    # Point 5 

    point_5_isen = {'SMASS': point_4['SMASS'],
                    'P': point_6['P'],
                    'refrigerant': cycle_inputs['refrigerant']}
    propriedades(point_5_isen)

    point_5 = {'P': point_6['P'],
               'HMASS': point_4['HMASS'] + (point_5_isen['HMASS'] - point_4['HMASS']) *cycle_inputs['expander_isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']}
    propriedades(point_5)
        


    # Point 1 
    point_1 = {'P': point_6['P'],
               'T': point_6['T'] + (e_hx*qmax_ffc)/point_6['C'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_1)
    
    # Point 2 
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


    upper_ef=1/(1+point_6['C']/point_3['C'])
  
    return {
        'm': m,
        'cooling':point_3['T']-point_4['T'],
        'q_evaporator': q_evaporator,
        'work': work,
        'cop': cop,
        'upper_ef':upper_ef,
        'slhx_exergy_destruction':slhx_exergy_destruction,
        'subcooling':point_3['T']-point_4['T'],
        'exergy_efficiency': cop / cop_carnot,
        'hx_efficiency':e_hx,
        'Total_destruction':total_exergy_destruction,
        'exergy_efficiency_components': 1 - total_exergy_destruction / work,
                
    }

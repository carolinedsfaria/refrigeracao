#Parallel cycle (CF)

#Importando bibliotecas
from CoolProp.CoolProp import PropsSI
import pandas as pd

from calculate_point import propriedades
   

def calculate_parallel_circuit_cycle(cycle_inputs):

    # Point 3 
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

    

    # Point 9 
    point_9 = {'Q': 1,
               'T': cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt'],
               'refrigerant': cycle_inputs['refrigerant']}
    propriedades(point_9)


    ######Calculate qmax########

    cp_min_fzc=min(point_3['C'],point_9['C'])
    qmax_fzc=cp_min_fzc*(point_3['T']-point_9['T'])
    e_hx=cycle_inputs['hx_efficiency']

    
    #Point 7
    

    point_7 = {'P': point_3['P'],
               'T': point_3['T'] - (e_hx*qmax_fzc)/point_3['C'],
               'refrigerant': cycle_inputs['refrigerant']
                  }
    propriedades(point_7)

            
    #Point 8
    point_8 = {'HMASS': point_7['HMASS'],
               'P': point_9['P'],
               'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_8)

    

    # Point 10 
    point_10 = {'P': point_9['P'],
                'T': point_9['T'] + (e_hx*qmax_fzc)/point_9['C'],
                'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_10)
    
    
    # Point 11
    point_11_isen = {'SMASS': point_10['SMASS'],
                     'P': point_3['P'],
                     'refrigerant': cycle_inputs['refrigerant']
                   }
    propriedades(point_11_isen)

    point_11 = {'P': point_3['P'],
                'HMASS': point_10['HMASS'] + (point_11_isen['HMASS'] - point_10['HMASS']) / cycle_inputs['isentropic_efficiency'],
                'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_11)


    
    q_evaporator=cycle_inputs['q_evaporator']
    m_lt = q_evaporator / (point_9['HMASS'] - point_8['HMASS'])
    work = m_lt * (point_11['HMASS'] - point_10['HMASS'])

 
    # COP    
    cop = (q_evaporator) / (work)
    
    
    # COP Carnot
    cop_carnot = cycle_inputs['t_internal_env_lt'] / (cycle_inputs['t_external'] - cycle_inputs['t_internal_env_lt'])

    
    # Exergy Destruction Components
    t_0 = cycle_inputs['t_external']
    
    compressor_exergy_destruction_lt = m_lt * t_0 * (point_11['SMASS'] - point_10['SMASS'])

    condenser_exergy_destruction_lt = m_lt * t_0 * (point_3['SMASS'] - point_11['SMASS'] + (point_11['HMASS'] - point_3['HMASS']) / cycle_inputs['t_external'])
    
    expansion_valve_lt_exergy_destruction = m_lt * t_0 * (point_8['SMASS'] - point_7['SMASS'])
    
    evaporator_lt_exergy_destruction = m_lt * t_0 * (point_9['SMASS'] - point_8['SMASS'] - (point_9['HMASS'] - point_8['HMASS']) / cycle_inputs['t_internal_env_lt'])
    
    slhx_exergy_destruction_lt = m_lt * ((point_9['HMASS']+point_3['HMASS'])-(point_7['HMASS']+point_10['HMASS'])+t_0 * (point_7['SMASS'] - point_3['SMASS']+point_10['SMASS'] - point_9['SMASS']))
                                               
    total_exergy_destruction = compressor_exergy_destruction_lt + condenser_exergy_destruction_lt + expansion_valve_lt_exergy_destruction + \
        evaporator_lt_exergy_destruction + slhx_exergy_destruction_lt

  
    
    
    cooling_FZC=point_3['T']-point_7['T']
    
    
    cycle_inputs['cooling_FZC']=cooling_FZC
    
    upper_ef=1/(1+point_9['C']/point_3['C'])
    return {
        
        'm_lt': m_lt,
        'q_evaporator': q_evaporator,
        'work': work,
        'cop': cop,
        'cooling_FZC':cooling_FZC,
        'exergy_efficiency': cop / cop_carnot,
        'compressor_exergy_destruction_lt':compressor_exergy_destruction_lt,
        'condenser_exergy_destruction_lt':condenser_exergy_destruction_lt,
        'expansion_valve_lt_exergy_destruction':expansion_valve_lt_exergy_destruction,
        'evaporator_lt_exergy_destruction':evaporator_lt_exergy_destruction, 
        'total_exergy_destruction':total_exergy_destruction,
        'exergy_efficiency_components': 1 - total_exergy_destruction / work,
        'T10':point_10['T'],
        'T7':point_7['T'],
        'T3':point_3['T'],
        'T9':point_9['T'],
        'upper_ef':upper_ef,
        'Eficiência do trocador':e_hx,
        'slhx_exergy_destruction_lt':slhx_exergy_destruction_lt,
        'minimum_ad':min(compressor_exergy_destruction_lt,condenser_exergy_destruction_lt,expansion_valve_lt_exergy_destruction,evaporator_lt_exergy_destruction,slhx_exergy_destruction_lt)

    }


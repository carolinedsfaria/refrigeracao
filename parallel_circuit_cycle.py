#Expander cycle with SLHX

#Importando bibliotecas
from CoolProp.CoolProp import PropsSI
import pandas as pd

from calculate_point import propriedades
   


# Calculates two evaporator parallel circuit cycle (q_evaporators or work as inputs)
def calculate_parallel_circuit_cycle(cycle_inputs):

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


    
    ## Identificar mistura azeotrópica

    t5=cycle_inputs['t_internal_env_ht'] - cycle_inputs['approach_evaporator_ht']
    x_5=cycle_inputs['x_5']    


    sat_liq={'Q': 0,
             'T': t5,
             'refrigerant': cycle_inputs['refrigerant']}
    propriedades(sat_liq)

    Pl_sat=sat_liq['P']

    sat_vap = {'Q': 1,
               'T': t5,
               'refrigerant': cycle_inputs['refrigerant']}
    propriedades(sat_vap)

    Pv_sat=sat_vap['P']


    if abs(Pl_sat-Pv_sat)>0: #mistura azeotrópica
            
        P=Pv_sat*x_5+(1-x_5)*Pl_sat

        point = {'Q':x_5,
                 'P': P,
                 'refrigerant': cycle_inputs['refrigerant']}

        propriedades(point)
        erro=t5-point['T']

        while abs(erro)>=10**(-3):
            P_5=point['P']+erro/10**(5)
            point = {'Q':x_5,
                     'P': P_5,
                     'refrigerant': cycle_inputs['refrigerant']}
            propriedades(point)
            erro=t5-point['T']

        point_5 = {'Q':x_5,
                   'P': point['P'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_5)

        #Point 4

        point_4 = {'P': point_3['P'],
                   'HMASS': point_5['HMASS'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_4)
        
            
        # Point 6 (after high temperature evaporator)

        point_6 = {'Q': 1,
                   'P':point_5['P'],
                   'refrigerant': cycle_inputs['refrigerant']}

        propriedades(point_6)




        ######Cálculo do x5 máximo########

            
        h5=point_3['HMASS']
        
        sat_liq={'Q': 0,
                 'T': cycle_inputs['t_internal_env_ht'] - cycle_inputs['approach_evaporator_ht'],
                 'refrigerant': cycle_inputs['refrigerant']}
        propriedades(sat_liq)

        hl_sat=sat_liq['HMASS']

        Pl_sat=sat_liq['P']

        sat_vap = {'Q': 1,
                   'T': cycle_inputs['t_internal_env_ht'] - cycle_inputs['approach_evaporator_ht'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(sat_vap)

        hv_sat=sat_vap['HMASS']
        Pv_sat=sat_vap['P']

        x_5=(h5-hl_sat)/(hv_sat-hl_sat)
        P_5=x_5*Pv_sat+(1-x_5)*Pl_sat
        t5=cycle_inputs['t_internal_env_ht'] - cycle_inputs['approach_evaporator_ht']

        point_5_max = {'HMASS':h5,
                       'P': P_5,
                       'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_5_max)
        erro=t5-point_5_max['T']

        while abs(erro)>=10**(-3):
            P_5=point_5_max['P']+erro/10**(5)
            point_5_max = {'HMASS':h5,
                           'P': P_5,
                           'refrigerant': cycle_inputs['refrigerant']}
            propriedades(point_5_max)
            erro=t5-point_5_max['T']

        point_5_max = {'HMASS':h5,
                       'P': point['P'],
                       'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_5_max)

        x5_max=point_5_max['Q']
        cycle_inputs['x5_max']=x5_max

    else: #fluido não azeotrópico

        # Point 6 (after high temperature evaporator)  
        point_6 = {'Q': 1,
                   'T': cycle_inputs['t_internal_env_ht'] - cycle_inputs['approach_evaporator_ht'],
                   'refrigerant': cycle_inputs['refrigerant']}

        propriedades(point_6)
            
        #Ponto 5
        point_5 = {'Q': cycle_inputs['x_5'],
                   'P': point_6['P'],
                   'refrigerant': cycle_inputs['refrigerant']
                       }
        propriedades(point_5)

        #Point 4

        point_4 = {'P': point_3['P'],
                   'HMASS': point_5['HMASS'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_4)

        ######Cálculo do x5 máximo########

        point_5_max = {'P': point_6['P'],
                       'HMASS': point_3['HMASS'],
                       'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_5_max)

        x5_max=point_5_max['Q']
        cycle_inputs['x5_max']=x5_max

    
    ########FFE cycle############


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
               'HMASS': point_1['HMASS'] + (point_2_isen['HMASS'] - point_1['HMASS']) / cycle_inputs['isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_2)

    q_evaporator_ht = cycle_inputs['q_evaporator_ht']
    m_ht = q_evaporator_ht / (point_6['HMASS'] - point_5['HMASS'])
    work_ht = m_ht * (point_2['HMASS'] - point_1['HMASS'])


    ########FZE cycle############

    
    ## Identificar mistura azeotrópica
    t8=cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt']
    x_8=cycle_inputs['x_8']
        
    sat_liq={'Q': 0,
             'T': t8,
             'refrigerant': cycle_inputs['refrigerant']}
    propriedades(sat_liq)

    Pl_sat=sat_liq['P']

    sat_vap = {'Q': 1,
               'T': t8,
               'refrigerant': cycle_inputs['refrigerant']}
    propriedades(sat_vap)

    Pv_sat=sat_vap['P']

    if abs(Pl_sat-Pv_sat)>0: #mistura azeotrópica
            
        P=Pv_sat*x_8+(1-x_8)*Pl_sat
            
        point = {'Q': x_8,
                 'P': P,
                 'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point)
        erro=t8-point['T']

        while abs(erro)>=10**(-3):
            P_8=point['P']+erro/10**(5)
            point = {'Q': x_8,
                     'P': P_8,
                     'refrigerant': cycle_inputs['refrigerant']}
            propriedades(point)
            erro=t8-point['T']

        point_8 = {'Q': x_8,
                   'P': point['P'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_8)

        #Point 7

        point_7 = {'P': point_3['P'],
                   'HMASS': point_8['HMASS'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_7)
            
        # Point 9 (after low temperature evaporator)      

        point_9 = {'Q': 1,
                   'P':point_8['P'],
                   'refrigerant': cycle_inputs['refrigerant']}

        propriedades(point_9)


        ######Cálculo do x8 máximo########

            
        h8=point_3['HMASS']
        
        sat_liq={'Q': 0,
                 'T': cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt'],
                 'refrigerant': cycle_inputs['refrigerant']}
        propriedades(sat_liq)

        hl_sat=sat_liq['HMASS']
        Pl_sat=sat_liq['P']

        sat_vap = {'Q': 1,
                   'T': cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(sat_vap)

        hv_sat=sat_vap['HMASS']
        Pv_sat=sat_vap['P']

        x_8=(h8-hl_sat)/(hv_sat-hl_sat)
        P_8=x_8*Pv_sat+(1-x_8)*Pl_sat
        t8=cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt']

        point_8_max = {'HMASS':h8,
                       'P': P_8,
                       'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_8_max)
        erro=t8-point_8_max['T']

        while abs(erro)>=10**(-3):
            P_8=point_8_max['P']+erro/10**(5)
            point_8_max = {'HMASS':h8,
                           'P': P_8,
                           'refrigerant': cycle_inputs['refrigerant']}
            propriedades(point_8_max)
            erro=t8-point_8_max['T']

        point_8_max = {'HMASS':h8,
                       'P': point['P'],
                       'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_8_max)

        x8_max=point_8_max['Q']
        cycle_inputs['x8_max']=x8_max

    else: #fluido não azeotrópico

        # Point 9 (after low temperature evaporator)  
        point_9 = {'Q': 1,
                   'T': cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt'],
                   'refrigerant': cycle_inputs['refrigerant']}

        propriedades(point_9)

        #Ponto 8
        point_8 = {'Q': cycle_inputs['x_8'],
                   'P': point_9['P'],
                   'refrigerant': cycle_inputs['refrigerant']
                       }
        propriedades(point_8)

        #Point 7

        point_7 = {'P': point_3['P'],
                   'HMASS': point_8['HMASS'],
                   'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_7)

        ######Cálculo do x8 máximo########

        point_8_max = {'P': point_9['P'],
                       'HMASS': point_3['HMASS'],
                       'refrigerant': cycle_inputs['refrigerant']}
        propriedades(point_8_max)

        x8_max=point_8_max['Q']
        cycle_inputs['x8_max']=x8_max


    # Point 10 (before compressor)
    point_10 = {'P': point_9['P'],
               'HMASS': point_9['HMASS']+point_3['HMASS']-point_7['HMASS'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_10)
    
    # Point 11 (after compressor)
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

    q_evaporator_lt = cycle_inputs['q_evaporator_lt']
    m_lt = q_evaporator_lt / (point_9['HMASS'] - point_8['HMASS'])
    work_lt = m_lt * (point_11['HMASS'] - point_10['HMASS'])
    work=work_ht+work_lt
  
    # COP    
    cop = (q_evaporator_ht + q_evaporator_lt) / (work)
    
    # COP Carnot
    cop_carnot_ht = cycle_inputs['t_internal_env_ht'] / (cycle_inputs['t_external'] - cycle_inputs['t_internal_env_ht'])
    cop_carnot_lt = cycle_inputs['t_internal_env_lt'] / (cycle_inputs['t_external'] - cycle_inputs['t_internal_env_lt'])
    
    w_carnot_ht = q_evaporator_ht / cop_carnot_ht
    w_carnot_lt = q_evaporator_lt / cop_carnot_lt
    
    cop_carnot = (q_evaporator_ht + q_evaporator_lt) / (w_carnot_ht + w_carnot_lt)
    
    # Exergy Destruction Components
    t_0 = cycle_inputs['t_external']
    
    compressor_exergy_destruction_ht = m_ht * t_0 * (point_2['SMASS'] - point_1['SMASS'])
    compressor_exergy_destruction_lt = m_lt * t_0 * (point_11['SMASS'] - point_10['SMASS'])
    compressor_exergy_destruction=compressor_exergy_destruction_ht+compressor_exergy_destruction_lt


    condenser_exergy_destruction_ht = m_ht * t_0 * (point_3['SMASS'] - point_2['SMASS'] + (point_2['HMASS'] - point_3['HMASS']) / cycle_inputs['t_external'])
    condenser_exergy_destruction_lt = m_lt * t_0 * (point_3['SMASS'] - point_11['SMASS'] + (point_11['HMASS'] - point_3['HMASS']) / cycle_inputs['t_external'])
    condenser_exergy_destruction=condenser_exergy_destruction_ht+condenser_exergy_destruction_lt

    
    expansion_valve_ht_exergy_destruction = m_ht * t_0 * (point_5['SMASS'] - point_4['SMASS'])
    expansion_valve_lt_exergy_destruction = m_lt * t_0 * (point_8['SMASS'] - point_7['SMASS'])
    expansion_valve_exergy_destruction=expansion_valve_ht_exergy_destruction+expansion_valve_lt_exergy_destruction

    
    evaporator_ht_exergy_destruction = m_ht * t_0 * (point_6['SMASS'] - point_5['SMASS'] - (point_6['HMASS'] - point_5['HMASS']) / cycle_inputs['t_internal_env_ht'])
    evaporator_lt_exergy_destruction = m_lt * t_0 * (point_9['SMASS'] - point_8['SMASS'] - (point_9['HMASS'] - point_8['HMASS']) / cycle_inputs['t_internal_env_lt'])
    evaporator_exergy_destruction=evaporator_ht_exergy_destruction+evaporator_lt_exergy_destruction

    
    slhx_exergy_destruction_ht = m_ht * ((point_3['HMASS']+point_6['HMASS'])-(point_1['HMASS']+point_4['HMASS'])+t_0 * (point_4['SMASS'] - point_3['SMASS']+point_1['SMASS'] - point_6['SMASS']))
    slhx_exergy_destruction_lt = m_lt * ((point_9['HMASS']+point_3['HMASS'])-(point_7['HMASS']+point_10['HMASS'])+t_0 * (point_7['SMASS'] - point_3['SMASS']+point_10['SMASS'] - point_9['SMASS']))
    slhx_exergy_destruction=slhx_exergy_destruction_ht+slhx_exergy_destruction_lt

                                               
    total_exergy_destruction = compressor_exergy_destruction + condenser_exergy_destruction + expansion_valve_exergy_destruction + \
        evaporator_exergy_destruction + slhx_exergy_destruction

    
    cooling_FFC=point_3['T']-point_4['T']
    cooling_FZC=point_3['T']-point_7['T']
    
    cycle_inputs['cooling_FFC']=cooling_FFC
    cycle_inputs['cooling_FZC']=cooling_FZC

                                               
    return {
        'x5_max':x5_max,
        'x8_max':x8_max,
        'm_ht': m_ht,
        'm_lt': m_lt,
        'q_evaporator_ht': q_evaporator_ht,
        'q_evaporator_lt': q_evaporator_lt,
        'work': work,
        'cop': cop,
        'cooling_FFC':cooling_FFC,
        'cooling_FZC':cooling_FZC,
        'exergy_efficiency': cop / cop_carnot,
        'total_exergy_destruction':total_exergy_destruction,
        'exergy_efficiency_components': 1 - total_exergy_destruction / work,        
        'x5':point_5['Q'],
        'x8':point_8['Q'],
        'minimum_ad':min(slhx_exergy_destruction_ht,slhx_exergy_destruction_lt,evaporator_ht_exergy_destruction,evaporator_lt_exergy_destruction,expansion_valve_ht_exergy_destruction,expansion_valve_lt_exergy_destruction,compressor_exergy_destruction_ht,compressor_exergy_destruction_lt,condenser_exergy_destruction_ht,condenser_exergy_destruction_lt,expansion_valve_ht_exergy_destruction,expansion_valve_lt_exergy_destruction),
    }


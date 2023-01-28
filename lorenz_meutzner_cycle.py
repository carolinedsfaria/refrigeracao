#Lorenz-Meutzner cycle 

from CoolProp.CoolProp import PropsSI
import pandas as pd

from calculate_point import propriedades


def calculate_lorenz_meutzner_cycle(cycle_inputs):

    # Point 3 (after condenser)
    point_3v = {'Q': 1,
                'T': cycle_inputs['t_external'] + cycle_inputs['approach_condenser'],
                'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_3v)


    point_3= {'Q': 0,
              'P': point_3v['P'],
              'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_3)


    # Point 7 (after low temperature evaporator)   
    point_7 = {'T': cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt'],
               'Q': 0.5,
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_7)



    # Point 9 (after high temperature evaporator)
    point_9 = {'Q': 1,
               'P':point_7['P'],
               'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_9)



    ######Calculate qmax########

    cp_min=min(point_3['C'],point_9['C'])
    qmax_ffc=cp_min*(point_3['T']-point_9['T'])
    e_hx=cycle_inputs['hx_efficiency']


    # Point 4 (after HTHX)

    point_4 = {'P': point_3['P'],
               'T': point_3['T'] - (e_hx*qmax_ffc)/point_3['C'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_4)

    # Point 1 (before compressor)


    point_1 = {'T': point_9['T']+(e_hx*qmax_ffc)/point_9['C'],
               'P': point_9['P'],
               'refrigerant': cycle_inputs['refrigerant']
                       }
    propriedades(point_1)     

    

    #Point 5 (before expansion device)

    h5=point_7['HMASS']+(point_4['HMASS']-point_9['HMASS'])/(1+(cycle_inputs['q_evaporator_ht']/cycle_inputs['q_evaporator_lt']))

    t5=(h5/point_3['HMASS'])*point_3['T']

    point_5 = {'P': point_3['P'],
               'T': t5,
               'refrigerant': cycle_inputs['refrigerant']
                  }
    propriedades(point_5)

    erro_point_5=h5-point_5['HMASS']
    while abs(erro_point_5)>=10**(-3):
        t5+=erro_point_5/(h5)           
        point_5 = {'P': point_3['P'],
                   'T': t5,
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        
        propriedades(point_5)
        erro_point_5=h5-point_5['HMASS']

    

    # Point 6 (before low temperature evaporator)

    h6=point_5['HMASS']

    
    liq_sat = {'Q': 0,
               'P': point_9['P'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(liq_sat)

    
    t6=(liq_sat['T']*h6)/liq_sat['HMASS']

    point_6 = {'T': t6,
               'P': point_9['P'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_6)
    
    erro_6= h6-point_6['HMASS']


    while abs(erro_6)>10**(-3):
        t6+=erro_6/h6
        point_6 = {'T': t6,
                   'P': point_9['P'],
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        propriedades(point_6)
        erro_6=h6-point_6['HMASS']



    # Point 8 (before high temperature evaporator)

    h8=(point_9['HMASS']+(cycle_inputs['q_evaporator_ht']/cycle_inputs['q_evaporator_lt'])*point_4['HMASS'])/(1+(cycle_inputs['q_evaporator_ht']/cycle_inputs['q_evaporator_lt']))

    point_8 = {'P': point_6['P'], 
               'T': point_7['T']*h8/point_7['HMASS'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_8)
    erro_point_8=h8-point_8['HMASS']

    while abs(erro_point_8)>=10**(-3):
        t_8=point_8['T']+erro_point_8/(h8)
            
        point_8 = {'P': point_6['P'],
                   'T': t_8,
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        propriedades(point_8)
        erro_point_8=h8-point_8['HMASS']
        
    # Point 2 (after compressor)
    s2=point_1['SMASS']

    point_2_sat = {'P': point_3['P'],
                   'Q': 1,
                   'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_2_sat)

    t2_sat=point_2_sat['T']
    s2_sat=point_2_sat['SMASS']
    t2_isen=t2_sat*s2/s2_sat

    point_2_isen = {'T': t2_isen, 
                    'P': point_3['P'],
                    'refrigerant': cycle_inputs['refrigerant']
                   }
    propriedades(point_2_isen)

    erro_point_2_isen=s2-point_2_isen['SMASS']

               
    while abs(erro_point_2_isen)>0.1:
        t_2_isen=point_2_isen['T']+erro_point_2_isen/(s2)#muito lento com 10**3 tentar com 10**6
            
        point_2_isen = {'P': point_3['P'],
                        'T': t_2_isen,
                        'refrigerant': cycle_inputs['refrigerant']
                  }
        propriedades(point_2_isen)
        erro_point_2_isen=s2-point_2_isen['SMASS']


    h2=point_1['HMASS'] + (point_2_isen['HMASS'] - point_1['HMASS']) / cycle_inputs['isentropic_efficiency']

    t2=(point_2_isen['T']*h2)/point_2_isen['HMASS']

    point_2 = {'P': point_3['P'],
               'T': t2,
               'refrigerant': cycle_inputs['refrigerant']
              }
    propriedades(point_2)

    erro_point_2=h2-point_2['HMASS']

               
    while abs(erro_point_2)>10**(-2):
        t2+=erro_point_2/(h2)
        point_2 = {'P': point_3['P'],
                   'T': t2,
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        propriedades(point_2)
        erro_point_2=h2-point_2['HMASS']


   

    # COP
    
    q_evaporator_ht = point_9['HMASS']-point_8['HMASS']
    q_evaporator_lt = point_7['HMASS']-point_6['HMASS']
    work_mass = point_2['HMASS'] - point_1['HMASS']
    cop = (q_evaporator_ht + q_evaporator_lt) / (work_mass)
    m = cycle_inputs['q_evaporator_lt'] / (point_7['HMASS'] - point_6['HMASS'])

    work=m*work_mass

    
    # COP Carnot
    cop_carnot_ht = cycle_inputs['t_internal_env_ht'] / (cycle_inputs['t_external'] - cycle_inputs['t_internal_env_ht'])
    cop_carnot_lt = cycle_inputs['t_internal_env_lt'] / (cycle_inputs['t_external'] - cycle_inputs['t_internal_env_lt'])
    
    w_carnot_ht = q_evaporator_ht / cop_carnot_ht
    w_carnot_lt = q_evaporator_lt / cop_carnot_lt
    
    cop_carnot = (q_evaporator_ht + q_evaporator_lt) / (w_carnot_ht + w_carnot_lt)



    # Exergy Analysis

    compressor_destruction=m*cycle_inputs['t_external']*(point_2['SMASS'] - point_1['SMASS'])
    condensador_destruction=m*cycle_inputs['t_external']*((point_3['SMASS'] - point_2['SMASS'])+(point_2['HMASS'] - point_3['HMASS'])/cycle_inputs['t_external'])
    hthx_destruction=m*((point_9['HMASS'] + point_3['HMASS'])-(point_1['HMASS'] + point_4['HMASS'])-cycle_inputs['t_external']*((point_3['SMASS'] + point_9['SMASS'])-(point_1['SMASS'] + point_4['SMASS'])))
    lthx_destruction=m*((point_4['HMASS'] + point_7['HMASS'])-(point_5['HMASS'] + point_8['HMASS'])-cycle_inputs['t_external']*((point_4['SMASS'] + point_7['SMASS'])-(point_5['SMASS'] + point_8['SMASS'])))
    expansion_valve_destruction=m*cycle_inputs['t_external']*(point_6['SMASS'] - point_5['SMASS'])
    evaporator_lt_destruction=m*cycle_inputs['t_external']*((point_7['SMASS'] - point_6['SMASS'])-(point_7['HMASS'] - point_6['HMASS'])/cycle_inputs['t_internal_env_lt'])
    evaporator_ht_destruction=m*cycle_inputs['t_external']*((point_9['SMASS'] - point_8['SMASS'])-(point_9['HMASS'] - point_8['HMASS'])/cycle_inputs['t_internal_env_ht'])

    total_exergy_destruction=compressor_destruction+condensador_destruction+hthx_destruction+lthx_destruction+\
                              expansion_valve_destruction+evaporator_lt_destruction+evaporator_ht_destruction
    
    exergy_efficiency_components=1-(total_exergy_destruction/work)
    exergy_efficiency=cop/cop_carnot

    
    cp9=point_9['C']
    cp3=point_3['C']
    r=cp9/cp3

    upper_ef=1/(1+r)
           
    
    return {
        'point_1':point_1,
        'point_2':point_2,
        'point_3':point_3,
        'point_4':point_4,
        'point_5':point_5,
        'point_6':point_6,
        'point_7':point_7,
        'point_8':point_8,
        'point_9':point_9,
        'm': m,
        'upper_efficiency':upper_ef,
        'q_evaporator_ht': q_evaporator_ht,
        'q_evaporator_lt': q_evaporator_lt,
        'work': work,
        'cop': cop,
        'hx_efficiency':e_hx,
        'r':r,
        'cp3':cp3,
        'cp9':cp9,
        'compressor_destruction':compressor_destruction,
        'condensador_destruction':condensador_destruction,
        'hthx_destruction':hthx_destruction,
        'lthx_destruction':lthx_destruction,
        'expansion_valve_destruction':expansion_valve_destruction,
        'evaporator_lt_destruction':evaporator_lt_destruction,
        'evaporator_ht_destruction':evaporator_ht_destruction,
        'total_exergy_destruction':total_exergy_destruction,
        'exergy_efficiency_components':exergy_efficiency_components,
        'exergy_efficiency': exergy_efficiency,
        

    }


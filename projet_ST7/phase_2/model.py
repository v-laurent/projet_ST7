from classes import *
from utils import *
from gurobipy import *
import matplotlib.pyplot as plt

def best_solution(employees,tasks,number_of_fake_tasks,threshold):
    number_of_unavailabilities=0
    for employee in employees[1:]:
        number_of_unavailabilities += len(employee.Unavailabilities)
    tasks = [0]+[t for t in tasks if t != 0]    
    
    number_of_employees,  number_of_tasks = len(employees)-1, len(tasks)-1

    #model
    m = Model('PL_phase_2')
    m.setParam('TimeLimit', 20*60)
    #decision variables
    DELTA = { (i,j,k) : m.addVar(vtype=GRB.BINARY, name=f'DELTA_{i}_{j}_{k}') 
            for i in range(1, number_of_tasks+1)
            for j in range(1, number_of_tasks+1)
            for k in range(1, number_of_employees+1) }

    T = { (k,i) : m.addVar(vtype=GRB.INTEGER, lb=480, ub=1440, name=f'T_{k}_{i}')
            for i in range(1, number_of_tasks+1)
            for k in range(1, number_of_employees+1) }

    P = { (k,i) : m.addVar(vtype=GRB.BINARY, name=f'P_{k}_{i}')
            for i in range(1, number_of_tasks+1)
            for k in range(1, number_of_employees+1) }

    X = { (i,j,k) : m.addVar(vtype=GRB.BINARY, name=f'X_{i}_{j}_{k}') 
            for i in range(1, number_of_tasks+1)
            for j in range(1, number_of_tasks+1)
            for k in range(1, number_of_employees+1) }

    #useful variables
    d = { (i,j,k) : distance(tasks[i], tasks[j])
            for i in range(1, number_of_tasks+1)  
            for j in range(1, number_of_tasks+1)  
            for k in range(1, number_of_employees+1) }

############# Constraints #############


    
    #temporal constraints
    oo = 1440
    lunch_duration=60
    temporal_constr = { (k,i,j) : m.addConstr( T[(k,j)] >= T[(k,i)] + tasks[i].TaskDuration +(3.6/(50*60)) * d[(i,j,k)] 
        -(1-DELTA[(i,j,k)])*oo +lunch_duration*X[(i,j,k)], 
        name=f'temporal_constr_{k}_{i}_{j}')
                            for i in range(1,number_of_tasks+1)
                            for j in range(number_of_employees+1,number_of_tasks+1)  #i in A*
                            for k in range(1,number_of_employees+1) }

#     temporal_constr = { (k,i,j) : m.addConstr( T[(k,j)] >= T[(k,i)] + tasks[i].TaskDuration +(3.6/(50*60)) * d[(i,j,k)] 
#         -(1-DELTA[(i,j,k)])*oo +lunch_duration*X[(i,j,k)], 
#         name=f'temporal_constr_{k}_{i}_{j}')
#                             for i in range(3,number_of_tasks+1)
#                             for j in range(number_of_employees+1,number_of_tasks+1)  #i in A*
#                             for k in [2] }
#     temporal_constr = { (k,i,j) : m.addConstr( T[(k,j)] >= T[(k,i)] + tasks[i].TaskDuration +(3.6/(50*60)) * d[(i,j,k)] 
#         -(1-DELTA[(i,j,k)])*oo +lunch_duration*X[(i,j,k)], 
#         name=f'temporal_constr_{k}_{i}_{j}')
#                             for i in [2]
#                             for j in range(number_of_employees+2,number_of_tasks+1)  #i in A*
#                             for k in [2] }
                        
    X_1_constr = { (i,j,k) : m.addConstr( X[(i,j,k)] >= DELTA[(i,j,k)] + P[(k,i)] - 1, name=f'X_1_constr_{i}_{j}_{k}')
                            for i in range(1,number_of_tasks+1)
                            for j in range(number_of_employees+1,number_of_tasks+1)  #i in A*
                            for k in range(1,number_of_employees+1) }

    X_2_constr = { (i,j,k) : m.addConstr( 2*X[(i,j,k)] <= DELTA[(i,j,k)] + P[(k,i)] , name=f'X_2_constr_{i}_{j}_{k}')
                            for i in range(1,number_of_tasks+1)
                            for j in range(number_of_employees+1,number_of_tasks+1)  #i in A*
                            for k in range(1,number_of_employees+1) }
       
    test_constr = { (i,k) : m.addConstr( P[(k,i)] <= quicksum([ DELTA[(i,j,k)] for j in range(number_of_employees+1,number_of_tasks+1) ]) )
                            for i in range(1,number_of_tasks+1)
                            for k in range(1,number_of_employees+1) }
        
    #all the employees have one and only one lunch time
    lunch_time_constr = {k : m.addConstr( quicksum([ P[(k,i)] for i in range(1, number_of_tasks+1) ]) == 1, name=f'lunch_time_constr_{k}')
                            for k in range(1, number_of_employees+1)}

    #the lunch time begins after 12am
    beggining_lunch_time_constr = {(k,i,j) : m.addConstr( T[(k,j)] >= 13*60*X[(i,j,k)], name = f'beggining_lunch_time_constr_{k}_{i}')
                                        for k in range(1, number_of_employees+1)
                                        for i in range(1, number_of_tasks+1)
                                        for j in range(1, number_of_tasks+1)  }
    #the lunch time begins before 13pm
    ending_lunch_time_constr = {(k,i) : m.addConstr( T[(k,i)] + tasks[i].TaskDuration <= 24*60 - 11*60*P[(k,i)], name = f'ending_lunch_time_constr_{k}_{i}')
                                        for k in range(1, number_of_employees+1)
                                        for i in range(1, number_of_tasks+1) }

    #task_available
    availability_task_lb_constr = { (i,k) : m.addConstr( tasks[i].OpeningTime <= T[(k,i)], name=f'avaibility_task_lb_constr_{i}_{k}' )
                                for i in range(1, number_of_tasks+1)
                                for k in range(1, number_of_employees+1) }

    availability_task_ub_constr = { (i,k) : m.addConstr( T[(k,i)] <= tasks[i].ClosingTime - tasks[i].TaskDuration , name=f'avaibility_task_ub_constr_{i}_{k}' )
                                for i in range(1, number_of_tasks+1)
                                for k in range(1, number_of_employees+1) }

    #employee_available
    availability_employee_lb_constr = { (i,k) : m.addConstr( employees[k].WorkingStartTime <= T[(k,i)], name=f'avaibility_employe_lb_constr_{i}_{k}' )
                                for i in range(3, number_of_tasks+1)
                                for k in range(1,number_of_employees+1) }


    avaibility_employee_ub_constr = { (i,k) : m.addConstr( T[(k,i)] <= employees[k].WorkingEndTime - tasks[i].TaskDuration - 3.6/(50*60)*d[(i,k,k)]*DELTA[(i,k,k)], name=f'avaibility_employe_ub_constr_{i}_{k}' )
                                for i in range(number_of_employees+number_of_unavailabilities+1,number_of_tasks+1)
                                for k in range(1,number_of_employees+1) }

    avaibility_employee_ub_constr = { (i,k) : m.addConstr( T[(k,i)] <= employees[k].WorkingEndTime - tasks[i].TaskDuration, name=f'avaibility_employe_ub_constr_{i}_{k}' )
                                for i in range(number_of_employees+1,number_of_employees+number_of_unavailabilities+1)
                                for k in range(1,number_of_employees+1) }

    #level constraint
    level_constr = {j : m.addConstr( quicksum( [ DELTA[(i,j,k)]*(employees[k].Level-tasks[j].Level) 
                                                    for i in range(1,number_of_tasks+1)  
                                                    for k in range(1,number_of_employees+1) ]) >= 0, name = f'level_{j}')
                        for j in range(1,number_of_tasks+1)    
                    }
    #beginning at the depot
    beginning_constr = {k : m.addConstr( quicksum([ DELTA[(k,i,k)] for i in range(1,number_of_tasks+1) ]) == 1, name = f'beginning_{k}')
                            for k in range(1, number_of_employees+1)}   

    #flow constraint
    flow_constr = {(k,t) : m.addConstr( quicksum( [DELTA[(i,t,k)] for i in range(1, number_of_tasks+1)] ) == quicksum( [DELTA[(t,j,k)] for j in range(1,number_of_tasks+1)] ), name=f'flow_{k}_{t}')
                        for t in range(1,number_of_tasks+1)
                        for k in range(1,number_of_employees+1) }  

    #some tasks have to be done by only one employee
    task_done_by_employee_constr = {t : m.addConstr( quicksum([ DELTA[(i,t, tasks[t].id_employee)] for i in range(1, number_of_tasks+1) ]) == 1, name=f'task_done_by_employee_{t}')
                                        for t in range(1, number_of_tasks+1) if tasks[t].id_employee != 0}
    
    task_not_done_by_others_constr = {t : m.addConstr( quicksum([ DELTA[(i,t, k)] for i in range(1, number_of_tasks+1) for k in range(1, number_of_employees+1) 
                                                                                  if k != tasks[t].id_employee]) == 0, name=f'task_not_done_by_others_{t}')
                                        for t in range(1, number_of_tasks+1) if tasks[t].id_employee != 0}

    
    #if one sub task is done, all the others have to stay unvisited
    family = 1
    subtask_constr = dict()
    while family < number_of_tasks+1:
        subtask_constr[family] = m.addConstr( quicksum([ DELTA[(i,j,k)] for i in range(1, number_of_tasks+1)
                                                                        for j in range(family, family + tasks[family].number_of_sisters+1)
                                                                        for k in range(1, number_of_employees+1) ]) <= 1, name=f'subtask_constr_{family}')
        family += tasks[family].number_of_sisters+1
    
    #threshold constraint 
    nb_tasks_done_expr = quicksum( DELTA[(i,j,k)] for i in range(1, number_of_tasks+1)
                                                    for j in range(1, number_of_tasks+1)
                                                    for k in range(1, number_of_employees+1))

    m.addConstr(nb_tasks_done_expr >= threshold, name='threshold_constr')

    
    m.addConstr(quicksum([DELTA[(i,i,k)] for i in range(1, number_of_tasks+1) for k in range(1, number_of_employees+1)]) == 0, name='threshold_constr')
        
        
    

    ##########  Objective ##########
    # 1st Objective function #
    """
    m.setObjective(quicksum(DELTA[(i,j,k)]*d[(i,j,k)] for i in range(1, number_of_tasks+1)
                                                    for j in range(1, number_of_tasks+1)
                                                    for k in range(1, number_of_employees+1)),GRB.MINIMIZE)
    """
    # 2nd objectif function #
    lambda1 = 0.0002
    lambda2 = 0.5
    m.setObjective( lambda2*quicksum([ DELTA[(i,j,k)]*tasks[j].TaskDuration for i in range(1, number_of_tasks+1)
                                                               for j in range(number_of_fake_tasks, number_of_tasks+1)
                                                               for k in range(1, number_of_employees+1) ]) 
                    - lambda1*quicksum([ DELTA[(i,j,k)]*d[(i,j,k)] for i in range(1, number_of_tasks+1)
                                                               for j in range(1, number_of_tasks+1)
                                                               for k in range(1, number_of_employees+1) ]),GRB.MAXIMIZE)

    #resolution
    m.update()
    #m.display()
    m.optimize()

    #returning the results
    if m.status == GRB.INFEASIBLE:
            return None

    DELTA = { (i,j,k) : DELTA[(i,j,k)].x
            for i in range(1, number_of_tasks+1)
            for j in range(1, number_of_tasks+1)
            for k in range(1,number_of_employees+1) }

    T = { (k,i) : T[(k,i)].x
            for i in range(1, number_of_tasks+1)
            for k in range(1, number_of_employees+1) }

    P = { (k,i) : P[(k,i)].x
            for i in range(1, number_of_tasks+1)
            for k in range(1, number_of_employees+1) }

    return DELTA, T, P, m.ObjVal, nb_tasks_done_expr.getValue()
    
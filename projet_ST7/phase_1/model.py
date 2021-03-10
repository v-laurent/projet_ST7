from classes import *
from utils import *
from gurobipy import *

def best_solution(employees,tasks):
    number_of_employees,  number_of_tasks = len(employees)-1, len(tasks)-1
    #model
    m = Model('PL_phase_1')

    #variables de décision
    DELTA = { (i,j,k) : m.addVar(vtype=GRB.BINARY, name=f'DELTA_{i}_{j}_{k}') 
            for i in range(number_of_tasks+1)
            for j in range(number_of_tasks+1)
            for k in range(1,number_of_employees+1) }

    T = { (k,i) : m.addVar(vtype=GRB.INTEGER, lb=480, ub=1440, name=f'T_{i}_{k}')
            for i in range(number_of_tasks+1)
            for k in range(1, number_of_employees+1) }

    #variables utiles
    d = { (i,j) : distance(tasks[i], tasks[j]) 
            for i in range(number_of_tasks+1)
            for j in range(number_of_tasks+1) }

    #contraintes

    #all the tasks have to be done
    tasks_done_constr = {i : m.addConstr( quicksum( [ DELTA[(i,j,k)] 
                                                        for j in range(number_of_tasks+1)
                                                        for k in range(1,number_of_employees+1) ]) == 1, name=f'task_done_constr_{i}')
                            for i in range(1, number_of_tasks+1)}

    #temporal constraints
    oo = 1440
    temporal_constr = { (k,i,j) : m.addConstr( T[(k,j)] >= T[(k,i)] + tasks[i].TaskDuration +(3.6/(50*60)) * d[(i,j)] -(1-DELTA[(i,j,k)])*oo, name=f'temporal_constr_{k}_{i}_{j}')
                            for i in range(number_of_tasks+1)
                            for j in range(1,number_of_tasks+1)
                            for k in range(1,number_of_employees+1) }

    #task_available
    avaibility_task_lb_constr = { (i,k) : m.addConstr( tasks[i].OpeningTime <= T[(k,i)], name=f'avaibility_task_lb_constr_{i}_{k}' )
                                for i in range(number_of_tasks+1)
                                for k in range(1,number_of_employees+1) }

    avaibility_task_ub_constr = { (i,k) : m.addConstr( T[(k,i)] <= tasks[i].ClosingTime - tasks[i].TaskDuration , name=f'avaibility_task_ub_constr_{i}_{k}' )
                                for i in range(number_of_tasks+1)
                                for k in range(1,number_of_employees+1) }

    #employee_available
    avaibility_employee_lb_constr = { (i,k) : m.addConstr( employees[k].WorkingStartTime <= T[(k,i)], name=f'avaibility_employe_lb_constr_{i}_{k}' )
                                for i in range(number_of_tasks+1)
                                for k in range(1,number_of_employees+1) }

    avaibility_employee_ub_constr = { (i,k) : m.addConstr( T[(k,i)] <= employees[k].WorkingEndTime - tasks[i].TaskDuration - (3.6/(50*60)) * d[(i,0)], name=f'avaibility_employe_ub_constr_{i}_{k}' )
                                for i in range(number_of_tasks+1)
                                for k in range(1,number_of_employees+1) }

    #level constraint
    level_constr = {j : m.addConstr( quicksum( [ DELTA[(i,j,k)]*(employees[k].Level-tasks[j].Level) 
                                                    for i in range(number_of_tasks+1)  
                                                    for k in range(1,number_of_employees+1) ]) >= 0, name = f'level_{j}')
                        for j in range(number_of_tasks+1)    
                    }
    #beginning at the depot
    beginning_constr = {k : m.addConstr( quicksum([ DELTA[(0,j,k)] for j in range(number_of_tasks+1) ]) == 1, name = f'beginning_{k}')
                            for k in range(1, number_of_employees+1)} 

    #ending at the depot
    ending_constr = {k : m.addConstr( quicksum([ DELTA[(i,0,k)] for i in range(number_of_tasks+1) ]) == 1, name = f'beginning_{k}')
                            for k in range(1, number_of_employees+1)}    

    #flow constraint
    flow_constr = {(k,t) : m.addConstr( quicksum( [DELTA[(i,t,k)] for i in range(number_of_tasks+1)] ) == quicksum( [DELTA[(t,j,k)] for j in range(number_of_tasks+1)] ), name=f'flow_{k}_{t}')
                        for t in range(number_of_tasks+1)
                        for k in range(1,number_of_employees+1) }  

    #objective
    m.setObjective(quicksum(DELTA[(i,j,k)]*d[(i,j)] for i in range(number_of_tasks+1)
                                                    for j in range(number_of_tasks+1)
                                                    for k in range(1,number_of_employees+1)),GRB.MINIMIZE)

    #resolution
    m.update()
    m.optimize()

    #returning the results
    DELTA = { (i,j,k) : DELTA[(i,j,k)].x
            for i in range(number_of_tasks+1)
            for j in range(number_of_tasks+1)
            for k in range(1,number_of_employees+1) }

    T = { (k,i) : T[(k,i)].x
            for i in range(number_of_tasks+1)
            for k in range(1, number_of_employees+1) }

    return DELTA, T
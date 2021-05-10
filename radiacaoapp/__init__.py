from numpy.linalg import solve as ls_solve
from copy import copy
from numpy import array,zeros
from scipy.constants import sigma

class radsurf:
    """Create a new Radiant Surface.
        
    e (float between 0 and 1) - Emissivity of the Radiant Surface
    
    A (float greater than 0) - Area of the Surface
    """
    total = 0
    list = []
    def __init__(self,e,A):
        self.num=radsurf.total
        self.e=e
        self.A=A
        radsurf.total=radsurf.total+1
        radsurf.list.append(self)
    @staticmethod
    def get(num):
        """ Returns a Radiant Surface by its number.
        
        num - number of the Radiant Surface"""
        if isinstance(num, list):
            ret = []
            for i in num:
                ret.append(radsurf.get(i))
            return ret
        for i in radsurf.list:
            if i.num==num:
                return radsurf.list[num]
    @staticmethod
    def K(num):
        """ Returns the 1st set of equation coefficient of a Radiant Surface by its number.

        num - number of the Radiant Surface"""
        sup = radsurf.get(num)
        if sup.e==1:
            return 1
        else:
            return (sup.e*sup.A)/(1-sup.e)
    @staticmethod
    def clear():
        """ Clears all Radiant Surfaces, Views and Couplings."""
        ans = input('All views and couplings will be cleared to, are you sure? (y/n)')
        if ans=='y':
            view.clear()
            cpl.clear()
            radsurf.list = []
            radsurf.total = 0
            print('All data cleared!')
        else:
            print('Kept all data without erasing anything')

class view:
    """Create a new view between two Radiant Surfaces (RDs).
        
    num_radsurf_dep: Number of the departure RD
    
    num_radsurf_arr: Number of the arrival RD
    
    F : The view factor from the departure RD to the arrival RD
    """
    total = 0
    list = []
    def __init__(self,num_radsurf_dep,num_radsurf_arr,F):
        self.num = view.total
        self.dep=radsurf.get(num_radsurf_dep)
        self.arr=radsurf.get(num_radsurf_arr)
        self.F=F
        view.total=view.total+1
        view.list.append(self)
    @staticmethod
    def get(num):
        """ Returns a view by its number.
        
        num - number of the view"""
        for i in view.list:
            if i.num==num:
                return view.list[num]
    @staticmethod
    def K(num):
        """ Returns the 2nd set of equation coefficient of a view by its number.

        num - number of the view"""
        vw = view.get(num)
        return vw.dep.A*vw.F
    @staticmethod
    def clear():
        """ Clears all Views."""
        view.list = []
        view.total = 0

class cpl:
    """Create a new coupling between multiple Radiant Surfaces (RDs).
        
    num_radsurf_list: List of the RDs numbers that belongs to the coupling
    
    q_gen: Heat generated inside de coupling (if not filled will be zero!)
    """
    total = 0
    list = []
    def __init__(self,num_radsurf_list,q_gen=0):
        self.num = cpl.total
        self.radsurf_list = radsurf.get(num_radsurf_list)
        self.q_gen = q_gen
        cpl.total=cpl.total+1
        cpl.list.append(self)
    @staticmethod
    def get(num):
        """Returns a coupling by its number."""
        for i in cpl.list:
            if i.num==num:
                return cpl.list[num]
    @staticmethod
    def clear():
        """Clears all couplings. """
        cpl.list = []
        cpl.total = 0

class load:
    """Create a load in a Radiant Surface

    num_radsurf: number of the Radiant Surface
    load_type: float - type of the load

        0 - Temperature given (default)
        1 - Heat flow given
        2 - Radiosity given

    value: value of the load
    """
    total = 0
    list = []
    def __init__(self, num_radsurf,value,load_type=0):
        self.num = load.total
        self.radsurf = radsurf.get(num_radsurf)
        self.type = load_type
        self.value = value
        load.total=load.total+1
        load.list.append(self)
    @staticmethod
    def get(num):
        """Returns a Load by its number"""
        for i in load.list:
            if i.num==num:
                return load.list[num]
    @staticmethod
    def clear():
        """Clear all Loads"""
        load.list = []
        load.total = 0

def gettemp(x):
    """
    Returns the temperature of a Radiant Surface given its Blackbody's Emissive Power

    x: Blackbody's Emissive Power of the Radiant Surface

    """
    return (x/sigma)**(1/4)

def mount():
    """
    Mounts the Linear System from scratch.

    Returns:

    A - A Matrix
    B - B independent vector of the LS
    """
    global n,A,B
    n = radsurf.total
    A = zeros([3*n,3*n])
    B = zeros([3*n])
    for i in radsurf.list:
        # first set of equations
        A[i.num,i.num] = radsurf.K(i.num)
        A[i.num,1*n+i.num] = - radsurf.K(i.num)
        if i.e!=1:
            A[i.num,2*n+i.num] = 1
        # second set of equations
        for j in view.list:
            if i.num==j.dep.num:
                A[1*n+i.num,j.dep.num] += view.K(j.num)
                A[1*n+i.num,j.arr.num] -= view.K(j.num)
            if i.num==j.arr.num:
                A[1*n+i.num,j.dep.num] -= view.K(j.num)
                A[1*n+i.num,j.arr.num] += view.K(j.num)
        A[1*n+i.num,2*n+i.num] = -1
    
    # writing couplings
    eq_counter = 0
    for i in cpl.list:
        num_radsurfs_coupled = len(i.radsurf_list)
        for j in range(0,num_radsurfs_coupled-1):
            A[2*n+eq_counter,1*n+i.radsurf_list[j].num] = 1
            A[2*n+eq_counter,1*n+i.radsurf_list[j+1].num] = -1 # em casos de proporcionalidades de poder emissivo colocar a constante de proporcionalidade aqui (upgrades futuros)
            eq_counter += 1
        for j in range(0,num_radsurfs_coupled):
            A[2*n+eq_counter,2*n+i.radsurf_list[j].num] = 1
        B[2*n+eq_counter] = i.q_gen
        eq_counter += 1

    # writing loads
    for i in load.list:
        # Temperature given
        if i.type==0:
            A[2*n+eq_counter+i.num,1*n+i.radsurf.num] = 1
            B[2*n+eq_counter+i.num] = sigma*i.value**4
        # Heat Flow given
        elif i.type==1:
            A[2*n+eq_counter+i.num,2*n+i.radsurf.num] = 1
            B[2*n+eq_counter+i.num] = i.value
        # Radiosity given
        elif i.type==2:
            A[2*n+eq_counter+i.num,0*n+i.radsurf.num] = 1
            B[2*n+eq_counter+i.num] = i.value
            
    return [A,B,n]

def solve():
    """Solves the Linear System (LS) with all Radiant Surfaces (RDs), view and couplings declared.

    mount command must be have been executed!

    Returns:

    A - A Matrix
    B - B independent vector of the LS
    X - X vector solved
    X_temperatures - X vector solved with the RDs temperatures placed in its emissive powers
    """
    global n,A,B

    # count of total equations for couplings
    # eq_counter = 0
    # for i in cpl.list:
    #     eq_counter += len(i.radsurf_list)
    # if eq_counter+load.total!=n:
    #     raise Exception("The Load quantity plus the number of Radiant Surfaces coupled is not equal to the number of Radiant Surfaces")
    
    # solution of the system and transformation from emissive power to temperature back again
    try:
        X = ls_solve(A,B)
        X_temperatures = copy(X)
        for i in range(0,n):
            X_temperatures[i+n] = gettemp(X[i+n])
    except:
        X = array([])
        X_temperatures = array([])
        raise Exception("System not solvable")
    return [A,B,X,X_temperatures]
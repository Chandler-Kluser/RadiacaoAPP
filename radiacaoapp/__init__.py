from numpy.linalg import solve as ls_solve
from copy import copy, error
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
        if (e>1 or e<=0):
            raise ValueError("Invalid Emissivity")
        if (A<0):
            raise ValueError("Invalid Area")
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
        if (F>1 or F<=0):
            raise ValueError("Invalid View Factor")
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
    def __init__(self,num_radsurf_list,q_gen=0,non_lin=0,non_lin_param=0,Temp_guess=[]):
        if (len(num_radsurf_list)<=1):
            raise ValueError("Couplings must have at least two Radiant Surfaces")
        if (not(non_lin==0 or non_lin==1 or non_lin==2)):
            raise ValueError("Invalid Nonlinearity Coupling Option")
        if (non_lin!=0):
            if (non_lin_param<=0):
                raise ValueError("Invalid Nonlinearity Parameter (Conduction or Convection)")
            if (len(num_radsurf_list)>2):
                raise ValueError("Nonlinear Couplings must have only two Radiant Surfaces")
            if (len(Temp_guess!=2)):
                raise ValueError("There must be only two Temperatures in Temperatures Guess List")
            for i in Temp_guess:
                if (i<=0):
                    raise ValueError("Guess Temperatures must be greater than zero")
        self.num = cpl.total
        self.radsurf_list = radsurf.get(num_radsurf_list)
        self.q_gen = q_gen
        self.non_lin = non_lin
        self.non_lin_param = non_lin_param
        self.Temp_guess = Temp_guess
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
        if (not(load_type==0 or load_type==1 or load_type==2)):
            raise ValueError("Incorrect Load Type")
        if ((load_type==0 or load_type==2) and value<=0):
            raise ValueError("Incorrect Load Value for this Type")
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

def GetTemp(x):
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
    
    # writing couplings - third set of equations (part 1/2)
    eq_counter = 0
    for i in cpl.list:
        num_radsurfs_coupled = len(i.radsurf_list)

        if (i.non_lin==0):      # Linear Coupling (2 or more Radiant Surfaces)
            for j in range(0,num_radsurfs_coupled-1):
                A[2*n+eq_counter,1*n+i.radsurf_list[j].num] = 1
                A[2*n+eq_counter,1*n+i.radsurf_list[j+1].num] = -1 # in cases of proportional emissive powers in couplings, write code here to improve generality
                eq_counter += 1
        elif (i.non_lin==1):    # Conductive Coupling (2 Radiant Surfaces)
            A[2*n+eq_counter,1*n+i.radsurf_list[0].num] = i.non_lin_param/(sigma*(i.Temp_guess[0]**3))      #   k / { sigma * T0^3 }
            A[2*n+eq_counter,1*n+i.radsurf_list[1].num] = -i.non_lin_param/(sigma*(i.Temp_guess[1]**3))     # - k / { sigma * T1^3 }
            A[2*n+eq_counter,2*n+i.radsurf_list[1].num] = -1                                                # - q1
            eq_counter += 1
        elif (i.non_lin==2):    # Convective Coupling (2 Radiant Surfaces)
            A[2*n+eq_counter,1*n+i.radsurf_list[0].num] = i.non_lin_param/(sigma*(i.Temp_guess[0]**3))      #   k / { sigma * T0^3 }
            A[2*n+eq_counter,1*n+i.radsurf_list[1].num] = -i.non_lin_param/(sigma*(i.Temp_guess[1]**3))     # - k / { sigma * T1^3 }
            A[2*n+eq_counter,2*n+i.radsurf_list[1].num] = -1                                                # - q1
            eq_counter += 1

        for j in range(0,num_radsurfs_coupled): # heat balance - the same for all 03 cases
            A[2*n+eq_counter,2*n+i.radsurf_list[j].num] = 1
        B[2*n+eq_counter] = i.q_gen
        eq_counter += 1

    # writing loads - third set of equations (part 2/2)
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

def SaveFile(filename):
    """
    Save all system information to a File
    """
    # erases previous content
    open(filename,'w').close()
    # creates a new file from scratch
    file = open(filename,'w')
    for i in radsurf.list:
        file.write("r,"+str(i.e)+","+str(i.A)+"\n")
    file.close()

def ReadFile(filename,createsObjects=False):
    """
    Read all system information in a File
    """
    file = open(filename,'r')
    lines = file.readlines()
    for i in lines:
        if i[0]=="r":
            print("oeeeee tem r\n")
        else:
            print("deu merdaaaaaa mmmm")
    file.close()

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
    if (A.shape[0]!=A.shape[1]):
        raise ValueError("The number of Equations is not equal to the number of Variables.")

    # # check whether there is a non linear coupling ...
    # ok = True
    # for i in cpl.list:
    #     if (i.non_lin!=0 and ok):
    #         ok = False
    try:
        X = ls_solve(A,B)
        X_temperatures = copy(X)
        for i in range(0,n):
            X_temperatures[i+n] = GetTemp(X[i+n])
    except:
        X = array([])
        X_temperatures = array([])
        raise Exception("System not solvable")
    return [A,B,X,X_temperatures]
import numpy as np
import warnings


def simplex(type, A, B, C, D, M):

    # m -- number of restrictions
    # n -- number of variables
    (m, n)= A.shape

    basic_vars = []
    count = n

    # matrix with new variables
    R = np.eye(m)

    # values of the new variables
    P = B

    # artificial variables position indicator
    artificial= []

    for i in range(m):
        if D[i] == 1:		# <=
            # add the slack variable to objective function
            C = np.vstack((C, [[0]]))

            # regist the slack variable as basic variable
            count = count + 1
            basic_vars = basic_vars + [count-1]

            artificial = [artificial, 0]

        elif D[i] == 0:	# =
            # add the artificial variable to objective function with the big M value
            if type == 'min':
                C = np.vstack((C, [[M]]))
            else:
                C = np.vstack((C, [[-M]]))

            # regist the artificial variable as basic variable
            count = count + 1
            basic_vars = basic_vars + [count-1]

            artificial = [artificial, 1]
        elif D[i] == -1:  # >=
            # add the surplus and artificial variables to objective function
            if type == 'min':
                C = np.vstack((C, [[0], [M]]))
            else:
                C = np.vstack((C, [[0], [-M]]))

            R = repeatColumnNegative(R, count + 1 - n)
            P = insertZeroToCol(P, count + 1 - n)

            # regist the artificial variable as basic variable
            count = count + 2
            basic_vars = basic_vars + [count-1]

            artificial = [artificial, 0, 1]
        else:
            print("invalid case")

    # current vertex
    X = np.vstack((np.zeros((n, 1)), P))

    # add new variables to matrix A
    A = np.hstack((A, R))

    # simplex tableau
    st = np.vstack((np.hstack((-np.transpose(C), np.array([[0]]))), np.hstack((A, B))))

    # number of columns
    (rows, cols) = st.shape

    # basic_vars = ((n + 1):n+m)'

    print('\nsimplex tableau\n')
    print(st)
    print('\ncurrent basic variables\n')
    print(basic_vars)
    print('\noptimal point\n')
    print(X)

    # check if z != 0 (when there are artificial variables)
    z_optimal = np.matmul(np.transpose(C), X)

    print('\ncurrent Z\n\n', z_optimal)

    if z_optimal != 0:
        for i in range(m):
            if D[i] == 0 or D[i] == -1:
                if type == 'min':
                    st[0,:]= st[0,:] + M * st[1+i,:]
                else:
                    st[0,:]= st[0,:] - M * st[1+i,:]

        print('\ncorrected simplex tableau\n')
        print(st)

    iteration = 0
    while True:
    # for zz in range(2):
        if type == 'min':
            # select the more positive value
            w = np.amax(st[0, 0:cols-1])
            iw = np.argmax(st[0, 0:cols-1])
        else:
            # select the more negative value
            w = np.amin(st[0, 0:cols-1])
            iw = np.argmin(st[0, 0:cols-1])

        if w <= 0 and type == 'min':
            print('\nGlobal optimum point\n')
            break
        elif w >= 0 and type == 'max':
            print('\nGlobal optimum point\n')
            break
        else:
            iteration = iteration + 1

            print('\n----------------- Iteration {} -------------------\n'.format(iteration))

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                #print('row,cols', st[1:rows, cols-1] ,'/', st[1: rows, iw] )
                bi = st[1:rows, cols-1] 
                colPivot = st[1: rows, iw]
                #Evitar que divida si el divisor 'st[1: rows, iw]' es negativo  o <= 0
                Tarr = []
                for i in range(len(colPivot)):
                    print('colPivot', i, '->', colPivot[i])
                    if(colPivot[i]) <=0:
                        Tarr.append(np.inf)
                    else:
                        Tarr.append(bi[i]/colPivot[i])
                #T = st[1:rows, cols-1] / st[1: rows, iw]
                T = np.array(Tarr)
                print('T ',T)
            
            R = np.logical_and(T != np.inf, T >= 0)
            print('R', R)
            
            (k, ik) = minWithMask(T, R)
            print('k = ', k, ' ik =', ik)

            # current z row
            cz = st[[0],:]

            # pivot element
            pivot = st[ik+1, iw]

            # pivot row divided by pivot element
            prow = st[ik+1,:] / pivot
            print('oki',st[ik+1,:] / pivot)

            st = st - st[:, [iw]] * prow

            # pivot row is a special case
            st[ik+1,:]= prow

            # new basic variable
            print('b iw',ik, iw)
            basic_vars[ik] = iw

            print('\ncurrent basic variables\n')
            print(basic_vars)
            #break

            # new vertex
            basic = st[:, cols-1]
            X = np.zeros((count, 1))

            t = np.size(basic_vars)

            for k in range(t):
                X[basic_vars[k]] = basic[k+1]

            print('\ncurrent optimal point\n')
            print(X)

            # new z value
            C = -np.transpose(cz[[0], 0:count])

            z_optimal = cz[0, cols-1] + np.matmul(np.transpose(C), X)
            st[0, cols-1] = z_optimal

            print('\nsimplex tableau\n\n')
            print(st)

            print('\ncurrent Z\n\n')
            print(z_optimal)

    # check if some artificial variable is positive (infeasible solution)
    tv = np.size(artificial)
    for i in range(tv):
        if artificial[i] == 1:
            if X[n + i] > 0:
                print('\ninfeasible solution\n')
                break

    return (z_optimal[0, 0], X)


def minWithMask(x, mask):
    
    min = 0
    imin = 0

    n = np.size(x)

    for i in reversed(range(n)):
        if mask[i] == 1:
            if min == 0:
                min = x[i]
                imin = i
            else:
                if min > x[i]:
                    min = x[i]
                    imin = i
    return (min, imin)


def repeatColumnNegative(Mat, h):
    """Repeat column h multiplied by - 1"""
    (r, c) = Mat.shape
    Mat = np.hstack((Mat[:, 0:h-1], -Mat[:, [h-1]], Mat[:, h-1:c]))

    return Mat


def insertZeroToCol(col, h):
    """insert zero to column"""
    k = np.size(col)
    col = np.vstack((col[0:h-1, [0]], np.array([[0]]), col[h-1:k, [0]]))

    return col

if __name__ == '__main__':

    np.set_printoptions(suppress=True)
    (z, x) = simplex('min', np.array([[-2, 3], [3, 2]]),
                            np.array([[9], [12]]),
                            np.array([[2], [1]]),
                            np.array([[-1], [-1]]),
                  100)

		"""Descricao
		simplex(type, restriccionCoeficients, bi values, Zcoeficients,  )
    Arguments:
		
    type -> Pode ser 'max' or 'min'
    A    -- A matrix of the model (numpy array)
    B    -- B matrix of the model, column vector (numpy array)
    C    -- C matrix of the model, column vector (numpy array)
    D    -- column vector with the types of restrictions of the model (numpy array), 1 is <=, 0 is =, -1 is >=
            for <= restrictions do nothing
            for = restrictions add an artificial variables and a big M in the objective
            function (min --> +M , max --> -M)
            for >= restrictions multiply by -1
    M    -- big M value
    """

#Sample 1
# min f(x) = 4x1 +x2
# 3x1 + x2 = 3
# 4x1 + 3x2 >= 6
# x1 + 2x2 <= 4
#M = 100

"""(z, x) = simplex('min', np.array([[3, 1], [4, 3], [1, 2]]),
                            np.array([[3], [6], [4]]),
                            np.array([[4], [1]]),
                            np.array([[0], [-1], [1]]),
        					100)"""
    

			
#Exercicio 5:
    #M = 0
    #(z, x) = simplex('max', np.array([[0.5, -5.5, -2.5, -9], [0.5, -1.5, -0.5, 1], [1, 0,0, 0]]),
		#np.array([[0], [0], [1]]),
                  #np.array([[10], [-57], [-9], [-24]]),
                  #np.array([[0], [0], [0]]),
              #0)
#Sample 2
# min 4x1+5x2
# 0.5x1+0.3x2 <=2.67
# 0.1x1+0.2x2 <=1
# 0.4x1 +0.5x2 <=3
# M =100

"""(z, x) = simplex('min', np.array([[0.5, 0.3], [0.1, 0.2], [0.4, 0.5]]),
                            np.array([[2.67], [1], [3]]),
                            np.array([[4], [5]]),
                            np.array([[1], [1], [1]]),
                  100)"""

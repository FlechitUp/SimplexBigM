import numpy as np
import warnings


def simplex(type, A, B, C, D, M):

    basic_vars = []
    
    (m, n)= A.shape	#m = |restricoes| , n = |variables|
    count = n

    # matrix com novas vars
    R = np.eye(m)

    Btemp = B

    artificial= []	# as posicoes

    for i in range(m):
        if D[i] == '<=':	
            # agregar a var de folga a Z
            C = np.vstack((C, [[0]]))

            # colocar a var de folga como básica
            count = count + 1
            basic_vars = basic_vars + [count-1]

            artificial = [artificial, 0]

        elif D[i] == '=':
            # agregar a var artificial a Z com o valor M
            if type == 'min':
                C = np.vstack((C, [[M]]))
            else:
                C = np.vstack((C, [[-M]]))

            # colocar a var artificial como basica
            count = count + 1
            basic_vars = basic_vars + [count-1]

            artificial = [artificial, 1]
        elif D[i] == '>=':  # >=
            # adicionar o excedente e as vars artificiais a Z
            if type == 'min':
                C = np.vstack((C, [[0], [M]]))
            else:
                C = np.vstack((C, [[0], [-M]]))

            R = repeatColumnNegative(R, count + 1 - n)
            Btemp = colocarZeroToCol(Btemp, count + 1 - n)

            # regist the artificial variable as basic variable
            count = count + 2
            basic_vars = basic_vars + [count-1]

            artificial = [artificial, 0, 1]
        else:
            print("invalid case")

    # Atual vertex
    X = np.vstack((np.zeros((n, 1)), Btemp))

    # adicionar novas vars a A
    A = np.hstack((A, R))

    # simplex pela tabela
    st = np.vstack((np.hstack((-np.transpose(C), np.array([[0]]))), np.hstack((A, B))))

    (rows, cols) = st.shape

    # basic_vars = ((n + 1):n+m)'

    print('\nSimplex Pela Tabela\n')
    print(st)
    print('\nAtual vars basicas\n')
    print(basic_vars)
    print('\nPonto Otimo\n')
    print(X)

    # check if z != 0 (when there are artificial variables)
    z_optimal = np.matmul(np.transpose(C), X)

    print('\ncurrent Z\n\n', z_optimal)

    if z_optimal != 0:
        for i in range(m):
            if D[i] == '=' or D[i] == '>=':
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

            print('\n ********** Iteracao ',iteration ,'********** \n')

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                bi = st[1:rows, cols-1] 
                colPivot = st[1: rows, iw]
                # registra inf se o divisor e <= 0
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
            
            (k, ik) = minBlandWithMask(T, R)
            #print('k = ', k, ' ik =', ik)

            # Z novo
            cz = st[[0],:]

            pivot = st[ik+1, iw]

            # linha pivOt dividida por elemento pivOt
            prow = st[ik+1,:] / pivot
            st = st - st[:, [iw]] * prow

            # casos especiais
            st[ik+1,:]= prow

            # nova var basica
            #print('b iw',ik, iw)
            basic_vars[ik] = iw

            print('\nAtual variavel basica\n')
            print(basic_vars)

            basic = st[:, cols-1]
            X = np.zeros((count, 1))

            t = np.size(basic_vars)

            for k in range(t):
                X[basic_vars[k]] = basic[k+1]

            print('\nAtual otimo\n')
            print(X)

            # Novo resultado de Z
            C = -np.transpose(cz[[0], 0:count])

            z_optimal = cz[0, cols-1] + np.matmul(np.transpose(C), X)
            st[0, cols-1] = z_optimal

            print('\nSimplex pela Tabela\n')
            print(st)

            print('\natual Z\n\n')
            print(z_optimal)

    # verificar se alguma var artificial nao foi cerada (solução inviável)
    tv = np.size(artificial)
    for i in range(tv):
        if artificial[i] == 1:
            if X[n + i] > 0:
                print('\nSolucao inviavel\n')
                break

    return (z_optimal[0, 0], X)


def minBlandWithMask(x, mask):
    
    min = 0
    imin = 0

    n = np.size(x)

		#Regra de Bland :D >>  se acontece um empate, escolher o menor indice.
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
    # multiplicado por - 1
    (r, c) = Mat.shape
    Mat = np.hstack((Mat[:, 0:h-1], -Mat[:, [h-1]], Mat[:, h-1:c]))

    return Mat


def colocarZeroToCol(col, h):
    kpos = np.size(col)
    col = np.vstack((col[0:h-1, [0]], np.array([[0]]), col[h-1:kpos, [0]]))

    return col

if __name__ == '__main__':
    print('Simplex Big M pela tabela')
    np.set_printoptions(suppress=True)
    (z, x) = simplex('min', np.array([[-2, 3], [3, 2]]),
                            np.array([[9], [12]]),
                            np.array([[2], [1]]),
                            np.array([['>='], ['>=']]),
                  100)

"""Descricao
		simplex( type, A, bi, C, D, M )
    Arguments:
		
    type -> Pode ser 'max' or 'min'
    A    -> coeficientes das restricoes agrupados por arrays
    bi   -> valores bi de cada restricao 
    C    -> coeficientes da funcao objetivo
    D    -> simbolos de restricoes (<= , =, >=) 
    M    -> valor de big M, recomenda-se colocar 0 se nenhuma restricao e >= ou =
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

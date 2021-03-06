import numpy as np
import warnings


def simplex(type, A, B, C, D, M):

    (m, n)= A.shape	#m = |restricoes| , n = |variables|

    fZ = ''
    for j in range(0,n):
        fZ += '+'+str(C[j][0]) if (C[j][0])>0 else str(C[j][0]) 
        fZ += 'x'+str(j) + ' '
    print(' Funcao Objetivo: Z =',fZ)

    print(' Restricoes:', m)
    restricTem = ''
    for j in range (0, m):
        restricTem = ''
        Ri = '  R'+str(j+1)+':'
        for k in range (0,n):
            const = '+'+str(A[j][k]) if A[j][k] > 0  else str(A[j][k])
            restricTem += const+'x'+str(k)+' '
        restricTem += D[j][0] + str(B[j][0])
        print(Ri,restricTem)

    basic_vars = []
    
    
    count = n
    

    # matrix com novas vars
    R = np.eye(m)

    Btemp = B

    artificial= []	# as posicoes

    for i in range(m):
        if D[i] == '<=':	
            # agregar uma var de folga a Z
            C = np.vstack((C, [[0]]))

            # colocar a var de folga como básica
            count = count + 1
            basic_vars = basic_vars + [count-1]

            artificial = [artificial, 0]

        elif D[i] == '=':
            # agregar uma var artificial a Z com o valor M
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

    print('\n *************** Tabela inicial *************** \n')
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
        if type == 'min':
            #O valor mais positivo
            w = np.amax(st[0, 0:cols-1])
            iw = np.argmax(st[0, 0:cols-1])
        else:
            #O valor mais negativo
            w = np.amin(st[0, 0:cols-1])
            iw = np.argmin(st[0, 0:cols-1])

        if w <= 0 and type == 'min':
            print('\nPonto otimo Final\n')
            break
        elif w >= 0 and type == 'max':
            print('\nPonto otimo Final\n')
            break
        else:
            iteration = iteration + 1

            print('\n\n *************** Iteracao',iteration ,'***************')

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                bi = st[1:rows, cols-1] 
                colPivot = st[1: rows, iw]
                # registra inf se o divisor e <= 0
                Tarr = []
                for i in range(len(colPivot)):
                    #print('colPivot', i, '->', colPivot[i])
                    if(colPivot[i]) <=0:
                        Tarr.append(np.inf)
                    else:
                        Tarr.append(bi[i]/colPivot[i])
                T = np.array(Tarr)
            
            R = np.logical_and(T != np.inf, T >= 0)
            
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

            print('\n * Atual variavel basica: ', basic_vars)

            basic = st[:, cols-1]
            X = np.zeros((count, 1))

            t = np.size(basic_vars)

            for k in range(t):
                X[basic_vars[k]] = basic[k+1]

            print('\n * Atual otimo: ')
            print(X)

            # Novo resultado de Z
            C = -np.transpose(cz[[0], 0:count])

            z_optimal = cz[0, cols-1] + np.matmul(np.transpose(C), X)
            st[0, cols-1] = z_optimal

            print('\nSimplex pela Tabela\n')
            print(st)

            print('\n * Atual Z: ', z_optimal)

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
    print('\n ================= Simplex Big M pela tabela =================\n')
    np.set_printoptions(suppress=True)
    (z, x) = simplex('max', np.array([[0.5, -5.5, -2.5, -9], [0.5, -1.5, -0.5, 1], [1, 0,0, 0]]), #A 
                            np.array([[0], [0], [1]]),                                            #bi
                            np.array([[10], [-57], [-9], [-24]]),                                 #C
                            np.array([['<='], ['<='], ['<=']]),                                      #D
                  0)                                   #M

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

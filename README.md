# SimplexBigM
O método BigM implementado inclui a regra de Bland. Se acontece um empate na razão, a escolha da variável para sair da base será aquela do menor índice.

## Run:
  `$ python3 simplex5BigM.py`


## Descrição
		simplex( type, A, bi, C, D, M )
    
    Argumentos:
		
    type -> Pode ser 'max' or 'min'
    A    -> coeficientes das restricoes agrupados por arrays
    bi   -> valores bi de cada restricao 
    C    -> coeficientes da funcao objetivo
    D    -> simbolos de restricoes (<= , =, >=) 
    M    -> valor de big M. Recomenda-se colocar 0 se nenhuma restricao e >= ou =
    
## Exemplos:

  **1) Exercício da atividade 5:** 
  
    ![image](https://user-images.githubusercontent.com/9610486/120828555-47420100-c522-11eb-834e-7e5218c5f732.png)
    
    ```
    (z, x) = simplex('max', np.array([[0.5, -5.5, -2.5, -9], [0.5, -1.5, -0.5, 1], [1, 0,0, 0]]), #A 
                            np.array([[0], [0], [1]]),                                            #bi
                            np.array([[10], [-57], [-9], [-24]]),                                 #C
                            np.array([['='], ['='], ['=']]),                                      #D
                            0)                                                                   #M   
    ```
  
  **2) Sample:**
  
  ![image](https://user-images.githubusercontent.com/9610486/120829853-7efd7880-c523-11eb-8ab6-99e91a29679d.png)

  
   ```
  (z, x) = simplex('min', np.array([[0.5, 0.3], [0.1, 0.2], [0.4, 0.5]]),  #A
                            np.array([[2.67], [1], [3]]),                   #bi
                            np.array([[4], [5]]),                           #C
                            np.array([['<='], ['<='], ['<=']]),             #D
                  100)
   ```
   

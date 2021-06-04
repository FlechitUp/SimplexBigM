# :sparkles: SimplexBigM + Regra de Bland
O método BigM implementado inclui a regra de **Bland**. Se acontece um empate na razão, a escolha da variável para sair da base será aquela do menor índice.

## Run:
  `$ python3 simplex5BigM.py`


## Descrição:
    simplex( type, A, bi, C, D, M )
    
    Argumentos:
		
    type -> Pode ser 'max' or 'min'
    A    -> coeficientes das restricoes agrupados por arrays
    bi   -> valores bi de cada restricao 
    C    -> coeficientes da funcao objetivo
    D    -> simbolos de restricoes (<= , =, >=) 
    M    -> valor de big M. Recomenda-se colocar 0 se nenhuma restricao e >= ou =
    
   :exclamation: Não incluir variáveis de folga nem artificiais. 
    
## :pushpin: Exemplos:

  **1) Exercício da atividade 5:**   
    ![image](https://user-images.githubusercontent.com/9610486/120830181-da2f6b00-c523-11eb-854a-8a7337fb8dd0.png)

    O código py:
	```
    (z, x) = simplex('max', np.array([[0.5, -5.5, -2.5, -9], [0.5, -1.5, -0.5, 1], [1, 0,0, 0]]), #A 
                            np.array([[0], [0], [1]]),                                            #bi
                            np.array([[10], [-57], [-9], [-24]]),                                 #C
                            np.array([['<='], ['<='], ['<=']]),                                   #D
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
   
   
   **3) Sample:**
   
   ![image](https://user-images.githubusercontent.com/9610486/120831718-74dc7980-c525-11eb-90a9-6dd941aa4c3b.png)


   
   ```
   (z, x) = simplex('min', np.array([[-2, 3], [3, 2]]), #A 
                            np.array([[9], [12]]),       #bi
                            np.array([[2], [1]]),        #C
                            np.array([['>='], ['>=']]),  #D
                  100)
    ```

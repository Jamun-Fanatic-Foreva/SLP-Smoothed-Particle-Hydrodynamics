# Taylor Green Vortex Simulation

## PySPH Testing

| Simulation Number 	| Scheme 	|  PST  	|      Kernel     	| nx 	| perturb 	|  hdx 	| PST_Rh 	| PST_R_coeff 	| PST_n_exp 	|
|:-----------------:	|:------:	|:-----:	|:---------------:	|:--:	|:-------:	|:----:	|:------:	|:-----------:	|:---------:	|
|         00        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 30 	|   0.2   	| 1.33 	|  0.05  	|   1.00E-04  	|     4     	|
|         01        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	| 1.33 	|  0.05  	|   1.00E-04  	|     4     	|
|         02        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 70 	|   0.2   	| 1.33 	|  0.05  	|   1.00E-04  	|     4     	|
|         03        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 90 	|   0.2   	| 1.33 	|  0.05  	|   1.00E-04  	|     4     	|
|         04        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	| 1.33 	|   0.1  	|   1.00E-04  	|     4     	|
|         05        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	| 1.33 	|   0.2  	|   1.00E-04  	|     4     	|
|         06        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|   0.5  	|   1.00E-05  	|     4     	|
|         07        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|   0.5  	|   1.00E-03  	|     4     	|
|         08        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|   1  	|  0.05  	|   1.00E-04  	|     4     	|
|         09        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|   1.00E-04  	|     4     	|
|         10        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|   2  	|  0.05  	|   1.00E-04  	|     4     	|
|         11        	| 𝛿+ SPH 	|  TRUE 	|  QuinticSpline  	| 50 	|   0.2   	|  1.5 	|  0.05  	|   1.00E-04  	|     4     	|
|         12        	| 𝛿+ SPH 	|  TRUE 	|     Gaussian    	| 50 	|   0.2   	|  1.5 	|  0.05  	|   1.00E-04  	|     4     	|
|         13        	| 𝛿+ SPH 	|  TRUE 	|   CubicSpline   	| 50 	|   0.2   	|  1.5 	|  0.05  	|   1.00E-04  	|     4     	|
|         14        	| 𝛿+ SPH 	| FALSE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|   ///  	|     ///     	|    ///    	|
|         15        	|  𝛿 SPH 	| FALSE 	|  QuinticSpline  	| 50 	|   0.2   	|   1  	|   ///  	|     ///     	|    ///    	|
|         16        	|  EDAC  	| FALSE 	|  QuinticSpline  	| 50 	|   0.2   	|   1  	|   ///  	|     ///     	|    ///    	|
|         17        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|   1.00E-02  	|     4     	|
|         18        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|   5.00E-05  	|     4     	|
|         19        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|   5.00E-04  	|     4     	|
|         20        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|   2.00E-05  	|     4     	|
|         21        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|   2.00E-04  	|     4     	|
|         22        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|   1.00E-04  	|     3     	|
|         23        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|   1.00E-04  	|     2     	|
|         24        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|   1.00E-04  	|     6     	|
|         25        	| 𝛿+ SPH 	|  TRUE 	|   CubicSpline   	| 50 	|   0.2   	|   2  	|  0.05  	|   1.00E-04  	|     3     	|
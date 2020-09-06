# Taylor Green Vortex Simulation

## PySPH Testing

| Simulation Number 	| Scheme 	|  PST  	|      Kernel     	| nx 	| perturb 	|  hdx 	| PST_Rh 	|
|:-----------------:	|:------:	|:-----:	|:---------------:	|:--:	|:-------:	|:----:	|:------:	|
|         00        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 30 	|   0.2   	| 1.33 	|  0.05  	|
|         01        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	| 1.33 	|  0.05  	|
|         02        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 70 	|   0.2   	| 1.33 	|  0.05  	|
|         03        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 90 	|   0.2   	| 1.33 	|  0.05  	|
|         04        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	| 1.33 	|   0.1  	|
|         05        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	| 1.33 	|   0.2  	|
|         06        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	| 1.33 	|   0.5  	|
|         07        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	| 1.33 	|    1   	|
|         08        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|   1  	|  0.05  	|
|         09        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|  0.05  	|
|         10        	| 𝛿+ SPH 	|  TRUE 	| WendlandQuintic 	| 50 	|   0.2   	|   2  	|  0.05  	|
|         11        	| 𝛿+ SPH 	|  TRUE 	|  QuinticSpline  	| 50 	|   0.2   	|  1.5 	|  0.05  	|
|         12        	| 𝛿+ SPH 	|  TRUE 	|     Gaussian    	| 50 	|   0.2   	|  1.5 	|  0.05  	|
|         13        	| 𝛿+ SPH 	|  TRUE 	|   CubicSpline   	| 50 	|   0.2   	|  1.5 	|  0.05  	|
|         14        	| 𝛿+ SPH 	| FALSE 	| WendlandQuintic 	| 50 	|   0.2   	|  1.5 	|   ///  	|
|         15        	|  𝛿 SPH 	| FALSE 	|  QuinticSpline  	| 50 	|   0.2   	|   1  	|   ///  	|
|         16        	|  EDAC  	| FALSE 	|  QuinticSpline  	| 50 	|   0.2   	|   1  	|   ///  	|
This is an approximate cycle cover solver which uses a randomized algorithm. The maximum cycle size handled by this algorith is 5. This can be modified.

The input file format that this solver accepts is as below.

6
2 4
0 1 0 0 0 0
0 0 1 0 0 0
1 0 0 0 0 0
0 0 0 0 1 0
0 0 0 0 0 1
0 0 0 1 0 0

The first line represents the number of vertices in the graph.

The second line represents the vertices with a cost of 2. 
The case that this program was optimized for only contained vertices with costs of 1 and 2.
However, small modifications would easily allow it to handle vertices with any cost values.
I do not plan on adding this functionality currently.

The remaining line represents the matrix of edges connecting the vertice.
A 1 at row 1 column 2 would signify an edge from vertice 1 to vertice 2.
These edges are directed.

The program is called using the below format.

python solver.py file_name search_count

file_name represents the name of the input file.
serach_count is how much work you want the program to do. An higher number would produce more accurate results, but require more computation time. The default is 5000.


# How this program works

1. The program finds a set of strongly connected components (SCC). These are sets of vertices that can all reach eachother.
2. All vertices that cannot reach themselves within 5 steps are removed from the SCCs.
3. The program randomly chooses cycles in each SCC.
4. An LP solver is used to find the set of cycles that would lead to the highest coverage.


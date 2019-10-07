# -*- coding: utf-8 -*-


"""
Created on Sun Sep 29 00:39:57 2019

@author: Jinghao Wang
"""
# Import libraries
import networkx as nx
import numpy as np

# Read mtx format file
mtx = nx.read_edgelist('web-google.mtx')

# Draw the graph
G = nx.Graph(mtx)
# =============================================================================
# nx.draw(G, pos=nx.spring_layout(G), alpha=0.5, node_size=25, node_color='b')
# =============================================================================

# Calculate pagerank
pr = nx.pagerank(G, alpha=0.85)
print(pr)

# Put all the values from the pr dict into a list
pr_list = []

for key in pr:
    pr_list.append(pr[key])

# Use NumPy to calculate the max, min, mean and std
pr_np = np.array(pr_list)
print("max(pr)="+str(np.max(pr_np)),'\n'
      "min(pr)="+str(np.min(pr_np)),'\n'
      "mean(pr)="+str(np.mean(pr_np)),'\n'
      "std(pr)="+str(np.std(pr_np)))

# Divide pagerank value into 4 intervals and count the number in each interval
interval = (np.max(pr_np) - np.min(pr_np)) / 4

n_25=0
n_50=0
n_75=0
n_100=0
for key in pr:
    if pr[key] >= np.max(pr_np) - 1*interval:
        n_25 = n_25+1
    if pr[key] >= np.max(pr_np) - 2*interval and pr[key] < np.max(pr_np) - 1*interval:
        n_50 = n_50+1
    if pr[key] >= np.max(pr_np) - 3*interval and pr[key] < np.max(pr_np) - 2*interval:
        n_75 = n_75+1
    if pr[key] >= np.max(pr_np) - 4*interval and pr[key] < np.max(pr_np) - 3*interval:
        n_100 = n_100+1

print("There are " + str(n_25) + " pages ranking top 25%.",'\n'
      "There are " + str(n_50) + " pages ranking 25~50%.",'\n'
      "There are " + str(n_75) + " pages ranking 50-75%.",'\n'
      "There are " + str(n_100) + " pages ranking 75-100%.")


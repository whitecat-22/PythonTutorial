import networkx as nx
import matplotlib.pyplot as plt
import internallink


pages = internallink.main()

def show_network(pages:list):
    pages = list(pages)
    pages.insert(0, "strt_url")
    G = nx.DiGraph()
    nx.add_star(G, pages)
    nx.draw_networkx(G)
    plt.show()

show_network(pages)

  # 有向グラフ (Directed Graph)


#G.add_nodes_from(['a','b','c','d'])

#G.add_edges_from([('a','b'),('a','c'),('a','d'),('b','c'),('b','d'),('d','c')])

# G.nodes[頂点][属性キー] = 属性値
#G.nodes[1]['a'] = 'Alice'

# G.edges[辺][属性キー] = 属性値
#G.edges[1, 2]['b'] = 'Bob'

# G.succ[始点][終点][属性キー] = 属性値
#G.succ[2][3]['c'] = 'Carol'

# G.pred[終点][始点][属性キー] = 属性値
#G.pred[3][1]['d'] = 'Dave'

# 辺の削除
##G.remove_edge(3, 4)                    
#G.remove_edges_from([(1, 3), (2, 5)])

# 頂点の削除 (削除された頂点に接続されている辺も削除されます)
#G.remove_node(5)
#G.remove_nodes_from([3, 4])

# 指定したパス上の頂点と辺を追加
##nx.add_path(G, [1, 2, 3, 4, 5])  # 1 → 2 → 3 → 4 → 5

# 指定した閉路上の頂点と辺を追加
#nx.add_cycle(G, [1, 2, 3, 4, 5])  # 1 → 2 → 3 → 4 → 5 → 1

# 放射状に頂点と辺を追加

  # 1 → 2, 1 → 3, 1 → 4, 1 → 5

#nx.add_path(G, [3, 5, 4, 1, 0, 2, 7, 8, 9, 6])  # add_pathで順番にたどる
#nx.add_path(G, [3, 0, 6, 4, 2, 7, 1, 9, 8, 5])

# pos=nx.spring_layout(G)


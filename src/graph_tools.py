import numpy as np
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt



class GraphFunctions:
    def __init__(self, G, d_lmt, sr_np=None):
        self.G = G
        self.clean_d_lmt = d_lmt
        self.sr_np = sr_np

    def _clean_graph(self):
        # Clean nodes
        # Remove nodes with degree greater than 100
        if self.clean_d_lmt:
            print(f'Cleaning nodes with degree more than {self.clean_d_lmt}')
            nodes_to_remove = [node for node, degree in dict(self.G.degree()).items() if degree > self.clean_d_lmt]
            self.G.remove_nodes_from(nodes_to_remove)
    
        # Identify nodes with degree 0 (isolated nodes)
        isolated_nodes = [node for node, degree in dict(self.G.degree()).items() if degree == 0]
        self.G.remove_nodes_from(isolated_nodes) 

    def graph_simrank(self, importance_factor=0.9):
        self._clean_graph()

        np.random.seed(42)  
        self.sr = nx.simrank_similarity(self.G, importance_factor=importance_factor, max_iterations=1000000)

        sr_np = []
        for n in self.G:
            sr_np.append([self.sr[n][m] for m in self.G])

        self.sr_np = np.array(sr_np)


class PlotLib:
    def __init__(self, G, d_lmt):
        self.G = G
        self.fn = GraphFunctions(self.G, d_lmt)
    
    def plot_heatmap(self, sr_np):

        node_name = [prop['name'] for _, prop in self.G.nodes(data=True)]
        df_similarity = pd.DataFrame(sr_np, columns=node_name, index=node_name)

        plt.title('Similarity Matrix')
        plt.xlabel('Words')
        plt.ylabel('Words')
        plt.imshow(df_similarity, cmap='viridis', interpolation='nearest')
        plt.colorbar(label='Similarity')
        plt.xticks(range(len(node_name)), node_name, rotation=90)
        plt.yticks(range(len(node_name)), node_name)
        plt.tight_layout()

    def plot_graph_plt(self, clean=False, label=False, pr_scale=2, FA2=False, node_colors=None):

        if clean:
            self.fn._clean_graph()

        # Assigning different colors based on the node labels
        opt = ''
        if label == 'id':
            opt = 'light'
            
        label_color_map = {
            'JobCategory': f'{opt}orange',
            'Skill': f'{opt}blue',
            'Employment' : 'yellow',
            2: 'red',
            4: 'purple',
            # Add more colors and labels as needed
        }

        # Assign node colors based on labels
        if not node_colors:
            node_colors = [label_color_map[node[1]['semantic']] for node in self.G.nodes(data=True)]

        if label=='id':
            node_labels = {node: str(i) for i, node in enumerate(self.G.nodes())}
            node_labels = {node: prop['name']+ str(i) for i, (node, prop) in enumerate(self.G.nodes(data=True))}
        else:
            node_labels = {node: prop['name'] for node, prop in self.G.nodes(data=True)}

        # Scale PageRank values for node size (radius)
        rank = nx.pagerank(self.G)
        scale = 100/(max(rank.values()) ** pr_scale)
        node_size = [score ** pr_scale * scale for _, score in rank.items()]


        # Draw the graph
        pos =  nx.kamada_kawai_layout(self.G)
        nx.draw(
            self.G, pos, with_labels=label, 
            labels=node_labels, 
            node_color=node_colors, 
            edge_color='gray', 
            node_size=node_size, 
            width=.3)

    def plot_KDE(self, sr_np):
    
        import seaborn as sns

        similarity_array = sr_np.flatten()

        sns.histplot(similarity_array, kde=True, bins=30, color='skyblue')
        plt.title('Similarity KDE Distribution Plot')
        plt.xlabel('Similarity Scores')
        plt.ylabel('Density')

        plt.xticks(
            ticks=[i * 0.1 for i in range(11)],  # Set the ticks to range from 0 to 1 with step 0.1
            labels=[f'{i * 0.1:.1f}' for i in range(11)]  # Format the tick labels as strings
        )

        plt.tight_layout()


class SimRankLib(GraphFunctions):   

    def __init__(self, G, sr_np, nodeA, TH_setA, TH_setB, setA_Tag, setB_Tag):

        super().__init__(G, None, sr_np)

        self.nodeA = nodeA
        self.TH_setA = TH_setA
        self.TH_setB = TH_setB
        self.setA_Tag = setA_Tag
        self.setB_Tag = setB_Tag

    def get_node_index(self, node):
        nodes_list = list(self.G.nodes())
        node_index = nodes_list.index(node)

        return node_index

    def subgraph_highrank_cnctd_nodeA(self):
        '''
            return the most simillar nodes to nodeA in setA and
            their connectivity network to setB
        '''

        print(self)
        nodeA_id = self.get_node_index(self.nodeA)
        nodes_G = list(self.G.nodes())
        TH_setA = self.TH_setA
        setA_Tag = self.setA_Tag

        job_0_sim = self.sr_np[nodeA_id]
        self.top_n_id = np.argsort(job_0_sim)[::-1].tolist()
        self.top_n_setA_id = [id for id in self.top_n_id if self.G.nodes[nodes_G[id]]['semantic'] == setA_Tag][:TH_setA]
        self.top_n_setA = [nodes_G[id] for id in self.top_n_setA_id]

        connected_nodes_list = []
        for node in self.top_n_setA :
            connected_nodes_list += list(self.G.neighbors(node))
        connected_nodes_list = list(set(connected_nodes_list))

        selected_nodes = connected_nodes_list + self.top_n_setA

        # Create a subgraph based on the selected nodes
        sG = self.G.subgraph(selected_nodes).copy()

        connected_components = list(nx.connected_components(sG))

        # Find subgraphs that include the desired node
        subgraphs_with_node = [sG.subgraph(component) for component in connected_components if self.nodeA in component]
        new_G = nx.compose_all(subgraphs_with_node)
        # self.set_node_similarity_nodeA(sG)

        return new_G
    
    def rank_setB_for_nodeA(self):

        self.sG = self.subgraph_highrank_cnctd_nodeA()
        if not nx.is_connected(self.sG):
            print('Graph is disconnected')
            print('increse the TH')
            return
        self.sLib_sG = SimRankLib(
            self.sG, None,
            self.nodeA, 
            self.TH_setA, 
            self.TH_setB, 
            self.setA_Tag, 
            self.setB_Tag
            )

        self.sLib_sG.graph_simrank()
        self.sLib_sG.rank_setB_in_subgraph()
        self.sLib_sG.filter_to_setB_only()
        return self.sLib_sG.nodaeA_rank_setB_print()

    def rank_setB_in_subgraph(self):

        # comput degree similarity
        degree = np.sum(nx.to_numpy_array(self.G), axis=1)
        sr_d = self.sr_np 
        np.fill_diagonal(sr_d, 0)

        self.sr_d = sr_d


        similarity_list = np.argsort(self.sr_d, axis=None, )[::-1]
        self.node_pair = np.unravel_index(similarity_list, self.sr_d.shape)

    def filter_to_setB_only(self):

        setA_Tag = self.setA_Tag

        job_id_s = [id for id, (_, data) in enumerate(self.G.nodes(data=True)) if data['semantic'] == setA_Tag]


        node_pair = self.node_pair

        filtered_node = []
        filtered_edge = []

        for i, x in enumerate(node_pair[0]):
            y = node_pair[1][i]
            if self.sr_d[x][y] != 0:
            
                check = 0
                for id in [x, y]:
                    if not id in job_id_s and not id in filtered_node:
                        filtered_node.append(id)
                        check +=1

                        if check >= 1:
                            filtered_edge.append([x, y])
                            
        self.filtered_node = filtered_node
        self.filtered_edge = filtered_edge

    def nodaeA_rank_setB_print(self):

        filtered_node, filtered_edge = self.filtered_node, self.filtered_edge
        sr_np = self.sr_np

        names = [data['name'] for _, data in self.G.nodes(data=True)]
        semantics = [data['semantic'] for _, data in self.G.nodes(data=True)]
        job_title = nx.get_node_attributes(self.G, 'name')[self.nodeA]
        degree = np.sum(nx.to_numpy_array(self.G), axis=1)

        data = []
        print(f' Job Title:  {job_title}')
        print('-----------------------------------------------------------------------------------------------')
        for i, n in enumerate(filtered_node):
            r, c = filtered_edge[i]
            
            new_row ={
                'Recommendation': names[n], 
                'Semantic': semantics[n], 
                'Similarity': sr_np[r][c],
                'Degree': degree[n],
                }
            data.append(new_row)
# 
        # 
        df = pd.DataFrame(data)
        df = df.sort_values(by=['Degree', 'Similarity', ], ascending=[False, False])

        return job_title, df
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from SPARQLWrapper import SPARQLWrapper, JSON
from pyvis.network import Network



class ExtractGraph:
    def __init__(self, endpoint):
        self.endpoint = endpoint 
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)
        
    def query(self, query):
        self.sparql.setQuery(query)
        return self.sparql.queryAndConvert()
    
    def query_to_nodes(self, query, G=None, src=None):
        results = self.query(query)
        df = pd.DataFrame(results['results']['bindings'])

        if not G:
            G = nx.Graph()

        if df.empty:
            return G

        keys =    df.columns[2:].tolist()
        semantic = df.columns[0]
        
        for row in df.iterrows():
            values = [row[1][col]['value'] for col in df.columns[0:]]
            G.add_node(values[0], name=values[1], semantic=semantic ,keys=keys, values=values[1:])

            if src:
                G.add_edge(src, values[0])

        return G


class GraphLib:
    def __init__(self, endpoint):
        self.G = nx.Graph()
        self.db = ExtractGraph(endpoint)

    def _get_nodes(self, semantic):
        graph = self.G
        nodes_list = [node for node, data in graph.nodes(data=True) if data.get('semantic') == semantic]
        # values = [graph.nodes[node]['value'] for node in nodes_list]
        return nodes_list
    
    def _loop_edge_list(self):

        edge_list =self.edge_list
        node_limit =self.node_limit

        QI = QueryInterim()
        for i, (n1, n2, opt) in enumerate(edge_list):

            limits = node_limit[i]
            query = eval(f'QI.{n1}(limits[0]).query')

            self.G = self.db.query_to_nodes(query, self.G) 

            srcNodes = self._get_nodes(n1)  

            for ni in srcNodes:
                if opt:
                    for opt_i in opt:
                        query_2 = eval(f'QI.{n1}().{n2}(ni, limits[1], opt=opt_i)')
                        self.G = self.db.query_to_nodes(query_2, self.G, src=ni) 
                else:
                    query_2 = eval(f'QI.{n1}().{n2}(ni, limits[1])')
                    self.G = self.db.query_to_nodes(query_2, self.G, src=ni) 

        return self.G

    def graph_1(self, nEmployment=10, nJob=10, nSkill=10 ):
        '''
        Consider graph with following classes:
        - Employment: include information from employment, and skill
        - Job: include information from skill and company
        '''

        self.edge_list = [
            ['Employment', '_job', None],
        ]
        self.node_limit =[
            [nEmployment, nJob]
            ]

        return self._loop_edge_list()


    def graph_2(self, nEmployment=10, nJob=10, nSkill=10 ):
        '''
        Consider graph with following classes:
        - Employment
        - Company : extracted from employment
        - Person
        - Skill
        - Job
        '''

        self.edge_list = [
            ['Job', '_skill', None],
            ['Employment', '_skill', [0, 1]],
            ['Employment', '_job', None],
        ]
        self.node_limit =[
            [nJob, nSkill],
            [nEmployment, nSkill],
            [nEmployment, nJob]
            ]

        return self._loop_edge_list()


        return self.G
    
    def graph_3(self, d_lmt, nJob=10, nSkill=10):
        '''
        Graph for recommending competencses for JobTags
        - job
        - skill_job
        '''

        edge_list = [
            ['Job', '_skill'],
        ]
        node_limit =[[nJob, nSkill]]


        QI = QueryInterim()
        for i, (n1, n2) in enumerate(edge_list):

            limits = node_limit[i]
            query = eval(f'QI.{n1}(limits[0]).query')

            self.G = self.db.query_to_nodes(query, self.G) 

            srcNodes = self._get_nodes(n1)  

            for ni in srcNodes:

                query =QI.Job()._skill(ni, limits[1])
                self.G = self.db.query_to_nodes(query, self.G, src=ni) 


        self.fn = GraphFunctions(self.G, d_lmt)
        self.pl = PlotLib(self.G, d_lmt)

        return self.G


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
    
    def get_node_index(self, node):
        nodes_list = list(self.G.nodes())
        node_index = nodes_list.index(node)

        return node_index

    def graph_simrank(self, importance_factor=0.9):
        self._clean_graph()

        np.random.seed(42)  # Setting a seed for reproducibility
        self.sr = nx.simrank_similarity(self.G, importance_factor=importance_factor, max_iterations=1000000)
        # self.sr_np = nx.simrank_similarity_numpy(self.G)

        sr_np = []
        for n in self.G:
            sr_np.append([self.sr[n][m] for m in self.G])

        self.sr_np = np.array(sr_np)

class SimRankLib(GraphFunctions):   

    def __init__(self, G, sr_np, nodeA, TH_setA, TH_setB, setA_Tag, setB_Tag):

        super().__init__(G, None, sr_np)

        self.nodeA = nodeA
        self.TH_setA = TH_setA
        self.TH_setB = TH_setB
        self.setA_Tag = setA_Tag
        self.setB_Tag = setB_Tag

    def set_node_similarity_nodeA(self, sG):

        nodes_G = list(self.G.nodes())

        for n in self.top_n_setA_id:
            nodei = nodes_G[n]
            print(self.G.nodes[nodei]['name'], nodes_G[n])

        
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
    
    def rank_setB_in_subgraph(self):

        # comput degree* similarity
        degree = np.sum(nx.to_numpy_array(self.G), axis=1)
        sr_d = self.sr_np # degree[:, np.newaxis]+  degree[:, np.newaxis] * 
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

        # Print recommendation
        # ------------------------------------------------------------------------------------------------
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
                # 'Node id': n
                }
            data.append(new_row)
# 
        # 
        df = pd.DataFrame(data)
        df = df.sort_values(by=['Degree', 'Similarity', ], ascending=[False, False])
        # print(df.head(self.TH_setB))

        return job_title, df

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

class PlotLib:
    def __init__(self, G, d_lmt):
        self.G = G
        self.fn = GraphFunctions(self.G, d_lmt)
    
    def graph_pyvis(self, file_name, clean=True, label=False):  
        
        from constants import RESULT_PATH

        # Create a Pyvis Network instance
        net = Network(width='vw', height='1200px', notebook=True)

        # Add nodes and edges to the pyvis Network object
        for node, data in GL.G.nodes(data=True):
            semantic, name = data['semantic'], data['name']
            title= f'{semantic}: {name}'
            net.add_node(node, label=title)#, size=scaled_rank_nl[node])

        for edge in GL.G.edges():
            net.add_edge(edge[0], edge[1], width=2)

        # net.show_buttons()
        net.toggle_physics(True)
        net.show(RESULT_PATH + file_name)  
        
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
            'Job': f'{opt}blue',
            'Skill': f'{opt}green',
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


        # ForceAtlas2 layout
        pos =  nx.kamada_kawai_layout(self.G)
        G = self.G
        if FA2:
            import forceatlas2 as fa2
            try:
                pos = fa2.forceatlas2_networkx_layout(self.G, pos, niter=10) 
                G = self.G
            except AssertionError:
                G = self.G.to_undirected()
            pos = fa2.forceatlas2_networkx_layout(G, pos, niter=10) 


        # Draw the graph
        nx.draw(
            G, pos, with_labels=label, 
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

class QueryInterim:
    def __init__(self):
        pass

    def test(self):
        query = """
            SELECT ?class (COUNT(?instance) AS ?nodeCount)
            WHERE {
            ?instance a ?class.
            }
            GROUP BY ?class
        """
        return query
    
    def person_job(self):
        query = """
            PREFIX diaso: <https://pilot-interim.brox.de/ontologies/DIASO/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT DISTINCT ?c1_id ?c2_id ?cco_count
            WHERE { 
                ?cco a diaso:SkillCoOccurrence ;
                     diaso:forSkill ?c1 , ?c2 ;
                     diaso:coOccurrenceCount ?cco_count .
                FILTER( ?c1 != ?c2 ) .
                ?c1 a diaso:Skill_min4 ;
                    diaso:skillId ?c1_id .
                ?c2 a diaso:Skill_min4 ;
                    diaso:skillId ?c2_id .
                FILTER( xsd:integer(?c1_id) < xsd:integer(?c2_id) ) .
            }
        """
        return query
      
    def skill(self, filter=''):
        query =f"""
            PREFIX diaso: <https://pilot-interim.brox.de/ontologies/DIASO/>
            SELECT  ?Skill ?skillName ?skillLang ?SkillGroup
            WHERE {{
                ?Skill a diaso:Skill.
                ?Skill diaso:skillName ?skillName.
                ?Skill diaso:skillLang ?skillLang.
                {filter}
            }}

            order by ?Skill
            limit {LIMIT}
            """
        return query
    
    def company(self, filter=''):
        query =f"""
            PREFIX diaso: <https://pilot-interim.brox.de/ontologies/DIASO/>
            SELECT  ?Company

            WHERE {{
                ?Employment a diaso:Employment.
                ?Employment diaso:companyName ?Company.
                {filter}
            }}

            order by ?companyName
            limit {LIMIT}
            """
        
        return query
    
    def person(self, filter=''):
        query=f"""
            PREFIX diaso: <https://pilot-interim.brox.de/ontologies/DIASO/>
            SELECT  ?Person ?rel1
            WHERE {{
                ?Person a diaso:PoolMember.
                ?rel1 diaso:employee ?Person.
                {filter}
            }}

            limit {LIMIT}
            """
        
        return query

    class Job:
        def __init__(self, limit=1):
            # print(limit)
            
            self.query=f"""
                    PREFIX onto:<http://www.ontotext.com/>
                    PREFIX dwo:<https://ontologies.brox.de/dwt24/>
				    PREFIX dcterms:<http://purl.org/dc/terms/>

                    SELECT ?Job ?name {{
                        ?Job a dwo:JobCategory .
                        ?Job dcterms:title ?name.
                    }}
                limit {limit}
                """
                        # ?Job dwo:jobTitle ?name.

        def _skill(self, job_entitiy, limit):
            # print(job_entitiy, limit)
            
            query=f"""
                PREFIX onto:<http://www.ontotext.com/>
				PREFIX dwo:<https://ontologies.brox.de/dwt24/>
				PREFIX dcterms:<http://purl.org/dc/terms/>
                SELECT  ?Skill ?name
                WHERE {{
    				BIND(<{job_entitiy}> AS ?Job).
                    ?skip dwo:belongsToJobCategory ?Job.
                    ?skip dwo:involvesRelevantSkill ?Skill.
    				?Skill dcterms:title ?name.

                }}
               
                limit {limit}
                """
            # print(query)
            return query

    class Employment:
        
        def __init__(self, limit=1):
            self.query =f"""
                PREFIX diaso: <https://pilot-interim.brox.de/ontologies/DIASO/>

                SELECT  ?Employment ?companyName ?jobTitle ?startDate ?endDate
                WHERE {{
                    ?Employment a diaso:Employment.
                    ?Employment diaso:endDate ?endDate.
                    ?Employment diaso:startDate ?startDate.
                    ?Employment diaso:jobTitle ?jobTitle.
                }}

                order by ?Employment
                limit {limit}
                """

        def _skill(self, empl_entitiy, limit, opt=0):
            
            query=f"""
                PREFIX diaso: <https://pilot-interim.brox.de/ontologies/DIASO/>

                SELECT  ?Skill ?name ?lang
                WHERE {{
                    BIND(<{empl_entitiy}> AS ?Employment).
                    ?Employment a diaso:Employment.
                    ?Employment diaso:involvesSkill_top{opt} ?Skill.

                    ?Skill diaso:skillName ?name.
                    ?Skill diaso:skillLang ?lang.
                }}
                limit {limit}
                """
            return query
        
        def _job(self, empl_entitiy, limit):
            
            query=f"""
                PREFIX diaso: <https://pilot-interim.brox.de/ontologies/DIASO/>
                SELECT  ?Job ?name
                WHERE {{
                    BIND(<{empl_entitiy}> AS ?Employment).
                    ?Employment a diaso:Employment.
                    ?Employment diaso:hasJobTag ?Job.

                    ?Job diaso:jobTagName ?name.
                }}
                limit {limit}
                """
            return query
        
    class SkillGropup_0:
        def __init__(self):
            pass

        def _skill(self, cg_entitiy):
            
            query=f"""
                PREFIX diaso: <https://pilot-interim.brox.de/ontologies/DIASO/>
                PREFIX data: <https://pilot-interim.brox.de/data/>

                SELECT  ?Skill ?name 
                WHERE {{
                    BIND(data:SkillGroup_0_{cg_entitiy} AS ?SkillGroup_0).

                    ?SkillGroup_0 diaso:member ?Skill.
                    ?Skill diaso:skillName ?name.
                    }}
                """
            return query


if __name__ == "__main__":

    from constants import GRAPH_DB_ENDPOINT 

    NJ = 1
    NC = 20000
    D_LMT= NC
    SIM_LMT = .899
    
    GL = GraphLib(GRAPH_DB_ENDPOINT)
    # G = GL.graph_3(D_LMT, nJob=NJ, nSkill=NC) 
    G = GL.graph_3(20, nJob=50, nSkill=5) 
    print(G)

    # GL.pl.plot_graph_plt(clean=False)#, label=True)
    # plt.show()


    # GL.fn.graph_simrank()
    # sr = GL.fn.sr
    
    # # Add edges to the graph, weighted by the similarity scores
    # G2 = nx.Graph()
    # G2.add_nodes_from(G.nodes(data=True))
    
    # for i in sr:
    #     for j, value in sr[i].items():
    #         if i != j:
    #             if value > SIM_LMT:
    #                 G2.add_edge(i, j, weight=value)
    
    

    
    # fn=GraphFunctions(G2, None)
    # fn._clean_graph()

    # pl = PlotLib(G, None)
    # pl.graph_pyvis('pyvis_example.html')
    # pl.plot_graph_plt()
    # plt.show()

    


    # # components = [fn.G.subgraph(c).copy() for c in nx.connected_components(fn.G)]

    # # for idx,g in enumerate(components,start=1):
    # #     for n, d in g.nodes(data=True):
    # #         print(d['semantic'], d['name'])
    # #     print('--------------------------------')

        
import networkx as nx
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from graph_tools import GraphFunctions, PlotLib


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
    
    def jobCategory_skill(self, d_lmt, nJob=10, nSkill=10):
        '''
        Graph for recommending skills for job categories
        - JobCategory
        - JobCategory_Skill
        '''

        edge_list = [
            ['JobCategory', '_Skill'],
        ]
        node_limit =[[nJob, nSkill]]


        QI = QueryLib()
        for i, (n1, n2) in enumerate(edge_list):

            limits = node_limit[i]
            query = eval(f'QI.{n1}(QI.ns, limits[0]).query')

            self.G = self.db.query_to_nodes(query, self.G) 

            srcNodes = self._get_nodes(n1)  

            for ni in srcNodes:

                query =QI.JobCategory(QI.ns)._Skill(ni, limits[1])
                self.G = self.db.query_to_nodes(query, self.G, src=ni) 


        self.fn = GraphFunctions(self.G, d_lmt)
        self.pl = PlotLib(self.G, d_lmt)

        return self.G


class QueryLib:
    def __init__(self,):
        self.ns = '''
                    PREFIX onto:<http://www.ontotext.com/>
                    PREFIX dwo:<https://ontologies.brox.de/dwt24/>
		            PREFIX dcterms:<http://purl.org/dc/terms/>
                '''
           
    class JobCategory:
        def __init__(self, ns, limit=1):
            self.name_spaces = ns
            
            self.query=f"""
                    {self.name_spaces}

                    SELECT ?JobCategory ?name {{
                        ?JobCategory a dwo:JobCategory .
                        ?JobCategory dcterms:title ?name.
                    }}
                limit {limit}
                """

        def _Skill(self, job_entitiy, limit):
            
            query=f"""
                {self.name_spaces}
                
                SELECT  ?Skill ?name
                WHERE {{
    				BIND(<{job_entitiy}> AS ?JobCategory).
                    ?Job dwo:belongsToJobCategory ?JobCategory.
                    ?Job dwo:involvesRelevantSkill ?Skill.
    				?Skill dcterms:title ?name.

                }}
               
                limit {limit}
                """
            return query


    
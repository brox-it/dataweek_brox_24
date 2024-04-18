link: https://colab.research.google.com/github/brox-it/dataweek_brox_24/blob/main/notebooks/02_graph_ds_explore.ipynb

Empowering Knowledge Graphs with
<img src="images/robot.png" style="width:0.27778in" alt="image" />: A
Cost-Effective Workflow
-------


Linked data is a core element of <span acronym-label="SWT"
acronym-form="singular+short">SWT</span>, facilitating large-scale data
integration and reasoning. The <span acronym-label="KG"
acronym-form="singular+short">KG</span>, a key component of the Semantic
Web, has demonstrated significant power in various domains. The strength
of <span acronym-label="KG" acronym-form="singular+short">KG</span> lies
in data engineering, specifically in the construction of semantics
through the modelling of graph data and ontologies. Although
<span acronym-label="KG" acronym-form="singular+short">KG</span> has the
potential to revolutionise business operations, its integration into
industries such as manufacturing is still incomplete and has not yet
reached its full potential (Buchgeher et al. 2020). Several challenges
contribute to this incomplete integration, such as the difficulty of
integrating <span acronym-label="KG"
acronym-form="singular+short">KG</span> data with existing enterprise
systems, the demand for skilled developers, and the high costs
associated with implementing <span acronym-label="KG"
acronym-form="singular+short">KG</span> solutions. In addition, the
business value of <span acronym-label="KG"
acronym-form="singular+short">KG</span>s is not clearly defined in many
sectors.  
On the other hand, <span acronym-label="LLM"
acronym-form="singular+short">LLM</span> is another approach of various
technologies in knowledge engineering. The importance and growth of
<span acronym-label="LM" acronym-form="singular+short">LM</span> and
especially <span acronym-label="LLM"
acronym-form="singular+short">LLM</span> in the current decade is
highlighted by a survey assessing the popularity of different aspects of
knowledge engineering (Groth et al. 2023). This survey suggests that the
era of <span acronym-label="SWT"
acronym-form="singular+short">SWT</span> is stabilising, while the use
of <span acronym-label="LLM" acronym-form="singular+short">LLM</span> is
increasing. Looking ahead, a key question for the field is how to
continue to develop. Despite impressive results from
<span acronym-label="LLM" acronym-form="singular+short">LLM</span>,
uncertainties remain that are (Vrandečić 2023):  

- Output with hallucination (Welleck et al. 2019) and requires ground
  truth

- Expensive to train and operate

- Difficult to fix and update

- Difficult to audit and explain, which is necessary for domain analysis

- Inconsistent responses

- Struggles with low-resource languages  

As far as is known, the <span acronym-label="KG"
acronym-form="singular+short">KG</span>s do not have these problems.
Therefore, using <span acronym-label="KG"
acronym-form="singular+short">KG</span>s to generate AI solutions for
storing domain-specific knowledge still has great potential and
utility.  
In a synergistic combination, <span acronym-label="LLM"
acronym-form="singular+short">LLM</span>s methods have recently
contributed significantly to breakthroughs in <span acronym-label="KG"
acronym-form="singular+short">KG</span> construction, e.g. tasks like
named entity recognition, entity typing, entity linking, coreference
resolution, and relation extraction (Zhong et al. 2023). Moreover, deep
knowledge representation models refine <span acronym-label="KG"
acronym-form="singular+short">KG</span>s by addressing issues like
completing corrupt tuples, discovering new tuples within existing
graphs, and merging graphs from diverse sources. Several knowledge
bases, including TransOMCS, ASER, and huapu, have implemented automatic
<span acronym-label="KG" acronym-form="singular+short">KG</span>
construction methods (Zhong et al. 2023). We also firmly believe that
the construction of <span acronym-label="KG"
acronym-form="singular+short">KG</span>s with the support of
<span acronym-label="LLM" acronym-form="singular+short">LLM</span>s is a
promising and forward-looking approach.  
Given <span acronym-label="KG" acronym-form="singular+short">KG</span>s
enterprise’s technology readiness, our training is dedicated to
presenting a cost-effective workflow developed by brox-IT Solutions. The
solution emphasises the use of low-cost or open-source technologies. The
workshop also covers <span acronym-label="KG"
acronym-form="singular+short">KG</span>s construction through the
incorporation of <span acronym-label="LLM"
acronym-form="singular+short">LLM</span> techniques to automate the
process. This will not only streamline <span acronym-label="KG"
acronym-form="singular+short">KG</span>s construction, but also
highlight <span acronym-label="GML"
acronym-form="singular+short">GML</span> discoveries as an added value
to enterprise data. The aim is to help industries take their first steps
into this technology. This training is aimed specifically at
organisations interested in building an Enterprise
<span acronym-label="KG" acronym-form="singular+short">KG</span>s,
enabling them to demonstrate the value that <span acronym-label="KG"
acronym-form="singular+short">KG</span>s can bring to their business.  

#  Targeted audiences 

This training is aimed at individuals or groups within industries
interested in digitisation and seeking valuable use cases for
implementing <span acronym-label="KG"
acronym-form="singular+short">KG</span>s. It is designed for those with
minimal to no previous experience of <span acronym-label="KG"
acronym-form="singular+short">KG</span>s and data science, but who are
keen to integrate <span acronym-label="KG"
acronym-form="singular+short">KG</span>s into their organisation’s data
systems. Our primary intention is to provide a streamlined workflow that
will allow for the proof of concept of the <span acronym-label="KG"
acronym-form="singular+short">KG</span>s within organisations. This
workflow will minimise the complexity associated with exploring and
establishing <span acronym-label="KG"
acronym-form="singular+short">KG</span>s. In order to facilitate the
learning process, all training materials will be accessible via a GitHub
repository, allowing participants to actively engage with the content.
However, due to practical limitations in dealing with large numbers of
participants, feedback sessions during the training will address general
questions, while specific or in-depth questions will receive dedicated
support after the training, particularly if the number of participants
exceeds 15.

<div class="acronym">

</div>

# Reference

<div id="refs" class="references csl-bib-body hanging-indent"
entry-spacing="0">

<div id="ref-Buchgeher2020KnowledgeGI" class="csl-entry">

Buchgeher, Georg, David Gabauer, J. Martinez-Gil, and Lisa Ehrlinger.
2020. “Knowledge Graphs in Manufacturing and Production: A Systematic
Literature Review.” *IEEE Access* 9: 55537–54.
<https://api.semanticscholar.org/CorpusID:229210861>.

</div>

<div id="ref-groth2023knowledge" class="csl-entry">

Groth, Paul, Elena Simperl, Marieke van Erp, and Denny Vrandečić. 2023.
“Knowledge Graphs and Their Role in the Knowledge Engineering of the
21st Century.” In *Dagstuhl Reports*. Vol. 12. 9. Schloss
Dagstuhl-Leibniz-Zentrum für Informatik.

</div>

<div id="ref-vrande2023key" class="csl-entry">

Vrandečić, Denny. 2023. “Keynote: The Future of Knowledge Graphs in a
World of Large Language Models.”
[https://www.knowledgegraph.tech/speakers/denny-vrandecic-2/,
https://www.youtube.com/watch?v=WqYBx2gB6vA&t=1059s](https://www.knowledgegraph.tech/speakers/denny-vrandecic-2/, https://www.youtube.com/watch?v=WqYBx2gB6vA&t=1059s).

</div>

<div id="ref-welleck2019neural" class="csl-entry">

Welleck, Sean, Ilia Kulikov, Stephen Roller, Emily Dinan, Kyunghyun Cho,
and Jason Weston. 2019. “Neural Text Generation with Unlikelihood
Training.” *arXiv Preprint , Id: 1908.04319*.

</div>

<div id="ref-Zhong2023ACS" class="csl-entry">

Zhong, Lingfeng, Jia Wu, Qian Li, Hao Peng, and Xindong Wu. 2023. “A
Comprehensive Survey on Automatic Knowledge Graph Construction.” *ACM
Computing Surveys*.
<https://api.semanticscholar.org/CorpusID:256808669>.

</div>

</div>

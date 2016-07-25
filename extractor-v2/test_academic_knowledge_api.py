__author__ = 'valerio cosentino'

import requests
import json
from ConfigParser import SafeConfigParser


def main():
    parser = SafeConfigParser()
    parser.read('./AKA.config')

    url = "https://api.projectoxford.ai/academic/v1.0/evaluate?"
    expr = "expr=Composite(AA.AuN=='jordi cabot')&count=5&attributes=Ti,Y,CC,AA.AuN,F.FN,E"
    headers = {'Ocp-Apim-Subscription-Key': parser.get('tokens', '0')}
    myResponse = requests.get(url+expr, headers=headers)

    if(myResponse.ok):

        jData = json.loads(myResponse.content)

        entities = jData.get('entities')
        for e in entities:
            print e
    else:
      myResponse.raise_for_status()

if __name__ == '__main__':
    main()


# {u'AA':
# 	[
# 		{'AuN': 'jordi cabot'},
# 		{'AuN': 'robert clariso'},
# 		{'AuN': 'daniel riera'}],
# 		'E': '{
# 			"DN":"UMLtoCSP: a tool for the formal verification of UML/OCL models using constraint programming",
# 			"D":"We present UMLtoCSP, a tool for the formal verification of UML/OCL models. Given a UML class diagram annotated with OCL constraints, UMLtoCSP is able to automatically check several correctness properties, such as the strong and weak satisfiability of the model or the lack of redundant constraints. The tool uses Constraint Logic Programming as the underlying formalism and the constraint solver ECL i PS e  as the verification engine.",
# 			"S":[
# 				{"Ty":0, "U":"http://dl.acm.org/ft_gateway.cfm?id=1321737&type=pdf"},
# 				{"Ty":3,"U":"http://gres.uoc.edu/pubs/UMLtoCSP_ASE2007.pdf"},
# 				{"Ty":1,"U":"http://dl.acm.org/citation.cfm?id=1321737"},
# 				{"Ty":1,"U":"http://portal.acm.org/citation.cfm?id=1321737"}
# 				],
# 			"VFN":"Automated Software Engineering",
# 			"DOI":"10.1145/1321631.1321737"}',
# 			'F': [
# 				{'FN': 'class diagram'},
# 				{'FN': 'constraint programming'},
# 				{'FN': 'object constraint language'},
# 				{'FN': 'formal verification'},
# 				{'FN': 'unified modeling language'},
# 				{'FN': 'satisfiability'},
# 				{'FN': 'programming language'},
# 				{'FN': 'computer science'}
# 				],
# 			'CC': 64,
# 			'Ti': u'umltocsp a tool for the formal verification of uml ocl models using constraint programming',
# 			'Y': 2007,
# 			'logprob': -18.898
# }

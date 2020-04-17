
'''
     def load_scores(self):
        """
        Load scores from a JSON file
        """
        self.scores = {}
        try:
            fil = open("data/scores_file.json", "r")
        except IOError:
            return
        self.scores = json.load(fil)
        fil.close()
'''




'''
    def dump_scores(self, force=False):
        """
        Dump the scores to the JSON file
        """
        if self.gameCNT % 1 == 0 or force:
            fil = open("data/scores_file.json", "w")
            json.dump(self.scores, fil)
            fil.close()
            print("scores updated on local file.")
'''



# importing pandas as pd  
import pandas as pd  
  
# list of name, degree, score 
nme = ["aparna", "pankaj", "sudhir", "Geeku"] 
deg = ["MBA", "BCA", "M.Tech", "MBA"] 
scr = [90, 40, 80, 98] 
  
# dictionary of lists  
dict = {'name': nme, 'degree': deg, 'score': scr}  
    
df = pd.DataFrame(dict) 
    
df  
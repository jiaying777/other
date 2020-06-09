import pickle
class userdata:
    def __init__(self):
        with open('userid.pickle', 'rb') as file:
            self.df =pickle.load(file)
        
    def write(self,userid,idd):
        self.df[userid] = idd
        with open('userid.pickle', 'wb') as f:
            pickle.dump(self.df, f)
            
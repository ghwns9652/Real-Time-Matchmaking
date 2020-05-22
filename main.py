import random
import threading
import time
import hdbscan
from scipy.stats import skewnorm
from sklearn.cluster import DBSCAN

games = []
queue = []
novice = []
search_window = 50

class Party:
    def __init__(_self, dist):
        _self.player_stat = []
        _self.avg_mmr = 0
        _self.avg_exp = 0

        if(dist == "uniform"):
            _self.party_size = random.randrange(1, 6) #FIXME
        elif(dist == "skew"):
            _self.party_size = random.randrange(1, 6)
        for i in range(0, _self.party_size):
            _self.player_stat.append(Player(dist))
            _self.avg_mmr += _self.player_stat[i].mmr
            _self.avg_exp += _self.player_stat[i].exp
        _self.avg_mmr /= _self.party_size
        _self.avg_exp /= _self.party_size
        _self.gentime = time.time()


class Player:
    def __init__(_self, dist):
        if(dist == "uniform"):
            _self.mmr = random.randrange(1, 3000) #assume highest MMR is 3000
            _self.exp = random.randrange(1, 30000) #highest playtime is 27000 games (http://ifi.gg/leaderboards)
        elif(dist == "skew"):
            _self.mmr = skewnorm.rvs(5, 1000, 500, 1)#FIXME: don't know this is correct distribution
            _self.exp = skewnorm.rvs(100, 10, 8000, 1)#FIXME: don't know this is correct distribution

def generation(period, dist):
    global queue
    for i in range(1, period):
        queue.append(Party(dist))

# move unexperience noobies to novice list
# return length of the list
def remove_novice(candidate, novice):
    cnt = 0
    i = 0

    while(cnt != search_window):
        if(candidate[i].avg_exp < 15):
            novice.append(candidate[i])
            del candidate[i]
        else:
            i+=1
        cnt+=1

    return i 

def normal_sorting(candidate, games):
    mmr_sorted = candidate[0:len(candidate)]
    mmr_sorted.sort(key=lambda x: x.avg_mmr)

    num_game = len(mmr_sorted)//10
    for i in range(0, num_game):
        # FIXME: deviation of mmr can be not good, starvation for high mmr gamer
        games.append(mmr_sorted[10*i:10*(i+1)]) 
    
    for i in range(0, 10*num_game):
        candidate.remove(mmr_sorted[i])

def clustering(candidate, games):
    
    '''
        
        (candidate = array of waiting parties , games = parties which start games)

        1.convert candidate into the matrix shape of (len(candiate),num_features); features = (gen_time,avg_mmr)
        2.clustering = hdbscan.HDBSCAN(min_cluster_size=10).fit(matrix)
        3.sorting same labeling
        4.1,2,3 again
    
    '''
    cluster_obj = hdbscan.HDBSCAN(min_cluster_size=10)


def make_matches(func, candidate, games):
    if(func=="normal_sorting"):
        normal_sorting(candidate, games)
    elif(func=="clustering"):
        clustering(candidate, games)
    '''
    add some functions

    '''


def matchmaking(execution_time):
    global queue
    global games
    global novice
    start_ts = time.time()
    func="normal_sorting"
    

    while(time.time() - start_ts < execution_time):
        #if(len(novice) >= 10):
        #    make_matches(novice, games)
        if(len(queue) >= search_window):
            candidate = queue[0:search_window]
            del queue[0:search_window]
            #remove_novice(candidate, novice)
            make_matches(func, candidate, games)
            queue = candidate + queue
    

def main():
    t0 = threading.Thread(target=generation, args=(10000, "uniform"))
    t1 = threading.Thread(target=matchmaking, args=[3])
    t0.start()
    t1.start()


main()
time.sleep(3)

print(len(games))
print(games[0][0].avg_mmr)
print(games[0][0].avg_exp)
print(games[0][0].gentime)

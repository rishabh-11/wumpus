from pysat.solvers import Glucose3
from Agent import *

kb = Glucose3() #initialize the sat solver
kb_map = {}     # a dictionary to map attributes to an integer value
safe = []       # list to keep track of safe states i.e. states without a mine on them
visited = []    # list to keep track of the states visited by the agent

#function to find neighbours of a state
def find_neighbour(loc):
    neighbours=[]
    if loc[0]<4:
        neighbours.append([loc[0]+1,loc[1]])
    if loc[0]>1:
        neighbours.append([loc[0]-1,loc[1]])
    if loc[1]>1:
        neighbours.append([loc[0],loc[1]-1])
    if loc[1]<4:
        neighbours.append([loc[0],loc[1]+1])
    return neighbours

#function to initialize the knowledge base with preknown clauses
def init():
    global kb
    global kb_map
    num = 1
    #initialize kb_map
    # 4 attributes of a state i.e mine, percept =0, percept =1, percept >1 
    for i in range(1,5):
        for j in range(1,5):
            kb_map["M"+str(i)+str(j)]=num
            kb_map["=0"+str(i)+str(j)]=num+16
            kb_map["=1"+str(i)+str(j)]=num+32
            kb_map[">1"+str(i)+str(j)]=num+48
            num=num+1

    # [1,1] is a safe state
    kb.add_clause([-kb_map["M11"]])
    
    #each state can have only one value of percept
    for i in range(1,5):
        for j in range(1,5):
            kb.add_clause([kb_map["=0"+str(i)+str(j)], kb_map["=1"+str(i)+str(j)], kb_map[">1"+str(i)+str(j)]])
            kb.add_clause([-kb_map["=0"+str(i)+str(j)],-kb_map["=1"+str(i)+str(j)]])
            kb.add_clause([-kb_map[">1"+str(i)+str(j)],-kb_map["=1"+str(i)+str(j)]])
            kb.add_clause([-kb_map["=0"+str(i)+str(j)],-kb_map[">1"+str(i)+str(j)]])
            kb.add_clause([-kb_map["=0"+str(i)+str(j)],-kb_map["=1"+str(i)+str(j)],-kb_map[">1"+str(i)+str(j)]])
    
    for i in range(1,5):
        for j in range(1,5):
            
            #percept =0
            temp=[]
            neighbours=find_neighbour([i,j])
            temp.append(kb_map["=0"+str(i)+str(j)])
            for k in range(len(neighbours)):
                temp.append(kb_map["M"+str(neighbours[k][0])+str(neighbours[k][1])])
            kb.add_clause(temp)
            
            for k in range(len(neighbours)):
                temp1=[]
                temp1.append(-kb_map["=0"+str(i)+str(j)])
                temp1.append(-kb_map["M"+str(neighbours[k][0])+str(neighbours[k][1])])
                kb.add_clause(temp1)
            
            #percept =1
            temp2=[]
            temp2.append(-kb_map["=1"+str(i)+str(j)])
            for k in range(len(neighbours)):
                temp2.append(kb_map["M"+str(neighbours[k][0])+str(neighbours[k][1])])
            kb.add_clause(temp2)
            
            for k in range(len(neighbours)):
                for l in range(k+1,len(neighbours)):
                    temp3=[]
                    temp3.append(-kb_map["=1"+str(i)+str(j)])
                    temp3.append(-kb_map["M"+str(neighbours[k][0])+str(neighbours[k][1])])
                    temp3.append(-kb_map["M"+str(neighbours[l][0])+str(neighbours[l][1])])
                    kb.add_clause(temp3)
                    
            #percept >1
            temp4=[]
            temp4.append(-kb_map[">1"+str(i)+str(j)])
            for k in range(len(neighbours)):
                temp4.append(kb_map["M"+str(neighbours[k][0])+str(neighbours[k][1])])
            kb.add_clause(temp4)
            
            for k in range(len(neighbours)):
                temp5=[]
                temp5.append(-kb_map[">1"+str(i)+str(j)])
                temp5.append(-kb_map["M"+str(neighbours[k][0])+str(neighbours[k][1])])
                for l in range(len(neighbours)):
                    if(k==l):
                        continue
                    temp5.append(kb_map["M"+str(neighbours[l][0])+str(neighbours[l][1])])
                kb.add_clause(temp5)

#function to find minimum manhattan distance from [4,4] among all the safe and unvisited states
def minManhattan(curr):
    val=10
    num=[0,0]
    for i in safe:
        if i in visited:
            continue
        if (8-i[0]-i[1])<val:
            val=(8-i[0]-i[1])
            num=i
        elif (8-i[0]-i[1])==val:
            if (abs(i[0]-curr[0])+abs(i[1]-curr[1]))<(abs(num[0]-curr[0])+abs(num[1]-curr[1])):
                num=i
    return num

#function to calculate the actions to be taken to reach [a,b] from current location
def reach(curr,a,b):
    visited.append([a,b])
    parent={}                           #dictionary to keep track of parent of a particular state in bfs
    parent[(curr[0],curr[1])]=[0,0] 
    queue=[curr]                        #queue for applying bfs on visited list
    visitedq = []                       #list to keep track of visited states in the bfs
    flag=0
    traverse=[]
    ans=[]                              #list to store the sequence of actions to be taken
    while flag==0:
        top=queue.pop(0)
        visitedq.append(top)
        top_neighbours=find_neighbour(top)
        for i in top_neighbours:
            if i in visitedq:
                continue
            if i in visited:
                queue.append(i)
                parent[(i[0],i[1])]=top
                if i==[a,b]:
                    traverse=i
                    flag=1
                    break
                    
    visited.remove([a,b])
    while traverse!=curr:
        temp=parent[(traverse[0],traverse[1])]
        if temp[0]==traverse[0]:
            if (traverse[1]-1)==temp[1]:
                ans.append("Up")
            else:
                ans.append("Down")
        else:
            if (traverse[0]-1)==temp[0]:
                ans.append("Right")
            else:
                ans.append("Left")
        traverse=temp
                
    return ans

# function where the agent is simulated
def main():
    global kb
    global safe
    global visited
    final = []      # list to store the entire path except [4,4]
    final.append([1,1]) 
    ag = Agent()    
    init()
    safe.append([1,1])
    visited.append([1,1])
    
    while(ag.FindCurrentLocation()!=[4,4]):
        curr = ag.FindCurrentLocation()
        if curr==[3,4]:
            ag.TakeAction("Right")
            break
        elif curr==[4,3]:
            ag.TakeAction("Up")
            break
        percept = ag.PerceiveCurrentLocation()
        visited.append(curr)
        kb.add_clause([kb_map[percept+str(curr[0])+str(curr[1])]])
        for k in range(1,5):
            for l in range(1,5):
                if kb.solve(assumptions=[kb_map["M"+str(k)+str(l)]]) and not kb.solve(assumptions=[-kb_map["M"+str(k)+str(l)]]):
                    kb.add_clause([kb_map["M"+str(k)+str(l)]])
                if kb.solve(assumptions=[-kb_map["M"+str(k)+str(l)]]) and not kb.solve(assumptions=[kb_map["M"+str(k)+str(l)]]):
                    kb.add_clause([-kb_map["M"+str(k)+str(l)]])
                    if [k,l] not in safe:
                        safe.append([k,l])
        a,b=minManhattan(curr)
        if [a,b]==[0,0]:
            print("Ambiguous Input Given")
            return 0
        ans=reach(curr,a,b)
        for k in range(len(ans)):
            ag.TakeAction(ans[len(ans)-1-k])
            final.append(ag.FindCurrentLocation())
    print('\n')
    print("Path taken by the agent is as follows:")
    for i in final:
        print(i,"=>",end=" ")
    print([4,4],end=" ")    
    
if __name__=='__main__':
    main()

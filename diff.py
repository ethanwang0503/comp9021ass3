import re
from collections import deque
import math

class DiffCommandsError(Exception):
    def __init__(self):
        pass

class DiffCommands:
    def __init__(self, diff_file = None):
        try:
            self.data = ''
            self.groups=list()
            with open(diff_file ) as inputfile:
                for line in inputfile.readlines():
                    diffs = re.match('^(\d+),?(\d+)?([acd])(\d+),?(\d+)?$',line)
                    # wrong_1
                    if diffs is None:raise DiffCommandsError()
                    # wrong_2
                    if line == '\n':raise DiffCommandsError()
                    # wrong_3
                    if ' ' in line:raise DiffCommandsError()
                    self.groups.append(diffs.groups())
                    self.data += diffs.group()+'\n'
            if not self.diff_check():raise DiffCommandsError()
            self.data = self.data.strip('\n')
        except DiffCommandsError:
            print('    ...\ndiff.DiffCommandsError: Cannot possibly be the commands for the diff of two files')

    def __str__(self):
        return self.data

    def diff_check(self):
        nb,last_line,line=0,[],[]
        for group in self.groups:
            for e in group:
                if e in (None,'a','d','c'):
                    line.append(e)
                else:
                    line.append(int(e))
            #wrong_4
            if line[2] == 'd' and line[4] is not None:return False
            if line[2] == 'a' and line[1] is not None:return False
            #wrong_5,7
            if line[2] == 'd' and line[0] - 1 + nb!= line[3]:return False
            if line[2] == 'a' and line[0] + 1 + nb != line[3]:return False
            if line[2] == 'c' and line[0] + nb != line[3]:return False
            if line[2] == 'd':
                if line[1]:
                    nb -= line[1] - line[0] + 1
                else:
                    nb -= 1
            if line[2] == 'a':
                if line[4]:
                    nb += line[4] - line[3] +1
                else:
                    nb += 1
            if line[2] == 'c':
                #wrong_6
                if last_line and last_line[2] != 'c' and (line[0] -1) in (last_line[0],last_line[1]): return False
                if line[4]:
                    if line[1]:
                        nb += (line[4] - line[3]) - (line[1] -line[0])
                    else:
                        nb += (line[4] - line[3])
                elif line[1]:
                    nb -= (line[1] - line[0])
            last_line = line
            line=[]
        return True

class OriginalNewFiles:
    def __init__(self, file1 = None, file2 = None):
        self.file1_list, self.file2_list = [],[]
        with open(file1) as inputfile1, open(file2) as inputfile2:
            for line in inputfile1.readlines():
                self.file1_list.append(line)
            for line in inputfile2.readlines():
                self.file2_list.append(line)

    def is_a_possible_diff(self, diffcommands):
        new_list=self.file1_list
        commands = diffcommands.groups
        for c in commands[::-1]:
            comm=list()
            for e in c:
                if e in (None,'a','d','c'):
                    comm.append(e)
                else:
                    comm.append(int(e))
            if comm[2] == 'a':
                if comm[4] is not None:
                    new_list = new_list[:comm[0]] + self.file2_list[comm[3]-1:comm[4]] + new_list[comm[0]:]
                else:
                    new_list = new_list[:comm[0]] + self.file2_list[comm[3]-1:comm[3]] + new_list[comm[0]:]
            if comm[2] == 'c':
                if comm[1] is not None:
                    if comm[4] is not None:
                        new_list = new_list[:comm[0]-1] + self.file2_list[comm[3]-1:comm[4]] + new_list[comm[1]:]
                    else:
                        new_list = new_list[:comm[0]-1] + self.file2_list[comm[3]-1:comm[3]] + new_list[comm[1]:]
                else:
                    if comm[4] is not None:
                        new_list = new_list[:comm[0]-1] + self.file2_list[comm[3]-1:comm[4]] + new_list[comm[0]:]
                    else:
                        new_list = new_list[:comm[0]-1] + self.file2_list[comm[3]-1:comm[3]] + new_list[comm[0]:]
            if comm[2] == 'd':
                if comm[1] is not None:
                    new_list = new_list[:comm[0]-1] + new_list[comm[1]:]
                else:
                    new_list = new_list[:comm[0]-1] + new_list[comm[0]:]
        return new_list == self.file2_list
        

    def output_diff(self, diffcommands):
        for c in diffcommands.groups:
            comm=c[0]
            if c[1]:comm+=','+c[1]
            comm+=c[2]
            comm+=c[3]
            if c[4]:comm+=','+c[4]
            print(comm)
            comm=list()
            for e in c:
                if e in (None,'a','d','c'):
                    comm.append(e)
                else:
                    comm.append(int(e))

            if comm[2] == 'a':
                if comm[4] is not None:
                    for line in self.file2_list[comm[3]-1:comm[4]]:
                        print("> "+line,end='')
                else:
                    print("> "+self.file2_list[comm[3]-1],end='')
            if comm[2] == 'c':
                if comm[1] is not None:
                    if comm[4] is not None:
                        for line in self.file1_list[comm[0]-1:comm[1]]:
                            print("< "+line,end='')
                        print("---")
                        for line in self.file2_list[comm[3]-1:comm[4]]:
                            print("> "+line,end='')
                    else:
                        for line in self.file1_list[comm[0]-1:comm[1]]:
                            print("< "+line,end='')
                        print("---")
                        print("> "+self.file2_list[comm[3]-1],end='')
                else:
                    if comm[4] is not None:
                        print("< "+self.file1_list[comm[0]-1],end='')
                        print("---")
                        for line in self.file2_list[comm[3]-1:comm[4]]:
                            print("> "+line,end='')
                    else:
                        print("< "+self.file1_list[comm[0]-1],end='')
                        print("---")
                        print("> "+self.file2_list[comm[3]-1],end='')
            if comm[2] == 'd':
                if comm[1] is not None:
                    for line in self.file1_list[comm[0]-1:comm[1]]:
                            print("< "+line,end='')
                else:
                    print("< "+self.file1_list[comm[0]-1],end='')

    def output_unmodified_from_original(self, diffcommands):
        modified_line_list=[]
        for c in diffcommands.groups:
            if c[2] in ('d','c'):
                if c[1]:
                    for i in range(int(c[0]),int(c[1])+1):
                        modified_line_list.append(i)
                else:
                    modified_line_list.append(int(c[0]))
        line_nb = len(self.file1_list)
        line_list = [ i for i in range(line_nb+1) if i not in modified_line_list]

        last_i=0
        for i in line_list:
            if i == 0:
                pass
            elif i == last_i +1:
                print(self.file1_list[i-1],end='')
                last_i = i
            else:
                print("...")
                print(self.file1_list[i-1],end='')
                last_i = i
        else:
            if i != line_nb:
                print("...")

    def output_unmodified_from_new(self, diffcommands):
        modified_line_list=[]
        for c in diffcommands.groups:
            if c[2] in ('a','c'):
                if c[4]:
                    for i in range(int(c[3]),int(c[4])+1):
                        modified_line_list.append(i)
                else:
                    modified_line_list.append(int(c[3]))
        line_nb = len(self.file2_list)
        line_list = [ i for i in range(line_nb+1) if i not in modified_line_list]

        last_i=0
        for i in line_list:
            if i == 0:
                pass
            elif i == last_i +1:
                print(self.file2_list[i-1],end='')
                last_i = i
            else:
                print("...")
                print(self.file2_list[i-1],end='')
                last_i = i
        else:
            if i != line_nb:
                print("...")

    def get_all_diff_commands(self):
        grid = [[0]*(len(self.file1_list)+2)]
        grid+= [[0]+[ int(self.file1_list[j] == self.file2_list[i]) for j in range(len(self.file1_list))]+[0] for i in range(len(self.file2_list))]
        grid+= [[0]*(len(self.file1_list)+2)]
        grid[0][0]=1
        grid[len(grid)-1][len(grid[0])-1]=1

        LCS = [ [ grid[i][j] for j in range(len(grid[0]))] for i in range(len(grid)) ]
        for j in range(1,len(grid[0])): LCS[0][j] = LCS[0][j-1] + grid[0][j]
        for i in range(1,len(grid)): LCS[i][0] = LCS[i-1][0] + grid[i][0]
        for i in range(1,len(grid)):
            for j in range(1,len(grid[0])):
                if grid[i][j] ==1:
                    LCS[i][j] = grid[i][j] + min(LCS[i-1][j-1],LCS[i-1][j],LCS[i][j-1])
                else:
                    LCS[i][j] = max(LCS[i-1][j-1],LCS[i-1][j],LCS[i][j-1])
        LCS = [ [ LCS[i][j]*grid[i][j] for j in range(len(grid[0]))] for i in range(len(grid)) ]

        points_list = deque([[(i,j) for j in range(len(LCS[0])) for i in range(len(LCS)) if grid[i][j] == 1 and LCS[i][j] == n ] for n in range(1,LCS[len(LCS)-1][len(LCS[0])-1]+1)])
        paths = [ [point] for point in points_list.popleft() ]
        # nb = 1
        # for points in points_list:nb*= len(points)
        # print("!!!!!!!: ",int(math.log(nb,10)))
        while points_list:
            points = points_list.popleft()
            paths = [ path +[point] for point in points for path in paths if point[0] > path[-1][0] and point[1] > path[-1][1] ]

        commands_list=[]
        for path in paths:
            command=''
            last_point = None
            for point in path:
                if not last_point:
                    last_point = point
                    continue
                else:
                    if point[1] != last_point[1] +1 or  point[0] != last_point[0] + 1 :
                        if point[1] == 0 or point[0] ==0:
                            former=point[1]-last_point[1]
                            latter=point[0]-last_point[0]
                        else:
                            former=point[1]-last_point[1]-1
                            latter=point[0]-last_point[0]-1
                        if former == 0:
                            if latter == 1:
                                command+='{}a{}\n'.format(point[1]-1,point[0]-1)
                            else:
                                command+='{}a{},{}\n'.format(point[1]-1,point[0]-latter,point[0]-1)
                        elif latter ==0:
                            if former == 1:
                                command+='{}d{}\n'.format(point[1]-1,point[0]-1)
                            else:
                                command+='{},{}d{}\n'.format(point[1]-former,point[1]-1,point[0]-1)
                        else:
                            if former == 1:
                                if latter == 1:
                                    command+='{}c{}\n'.format(point[1]-1,point[0]-1)
                                else:
                                    command+='{}c{},{}\n'.format(point[1]-1,point[0]-latter,point[0]-1)
                            else:
                                if latter == 1:
                                    command+='{},{}c{}\n'.format(point[1]-former,point[1]-1,point[0]-1)
                                else:
                                    command+='{},{}c{},{}\n'.format(point[1]-former,point[1]-1,point[0]-latter,point[0]-1)
                last_point = point
            commands_list.append(command.strip('\n'))
        commands_list.sort()
        return commands_list
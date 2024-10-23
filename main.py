import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from tqdm import tqdm

def draw_from_dataset(dataset, prop):
    props = np.random.uniform(0, 1, len(dataset))
    mask = np.array(props <= 1-prop)
    index = range(len(dataset))
    compressed = np.ma.masked_array(index, mask).compressed()

    try:
        return np.array(dataset)[compressed]
    except IndexError:
        return []

class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.status = 0
        self.contageous_counter = 0
        self.mean_contageous_period = 10
        self.sdev_contageous_period = 3
        self.immune_counter = 0
        self.mean_immune_period = 50
        self.sdev_immune_period = 10
        self.kill_prop = 0.0001


    def __repr__(self):
        # this only enables us to work with a readable representation of the object
        # in this case, the status is all we need
        return repr(self.status)


    def make_susceptible(self):
        self.contageous_counter = 0
        self.status = 0

    def infect(self):
        self.status = 1

    def make_immune(self):
        self.status = 2

    def kill(self):

        self.status = 3

    # the get status function is called once per step so we can use it to count the number of time steps an agent is infected since the infect function was called
    def get_status(self):
        self.contageous_period = np.random.normal(loc=self.mean_contageous_period, scale=self.sdev_contageous_period)
        self.immune_period = np.random.normal(loc=self.mean_immune_period, scale=self.sdev_immune_period)

        if self.status == 1 and self.contageous_counter < self.contageous_period:
            self.contageous_counter += 1
            if self.contageous_counter >= self.contageous_period:
                sample = np.random.uniform(0, 1)
                if 1-self.kill_prop <= sample:
                    self.kill()
                else:
                    self.make_immune()
                self.contageous_counter = 0

        elif self.status == 2 and self.immune_counter < self.immune_period:
            self.immune_counter += 1
            if self.immune_counter >= self.immune_period:
                self.make_susceptible()
                self.immune_counter = 0

        return self.status


class Grid:
    def __init__(self, n):
        # initialize the grid
        self.n = n
        self.grid = np.empty((n,n), object)

        for i in range(self.n):
            for j in range(self.n):
                agent = Agent(i, j)
                # specify initial configuration
                if (i, j) == (0, 0):
                    agent.infect()
                else:
                    agent.make_susceptible()
                # the agent class has a __repr__ dunder method which returns the self.status instance variable
                self.grid[i, j] = agent
        #print(self.grid)


    def update(self, susceptible_list, infected_list, immune_list, killed_list):
        neighbors = []
        n_susceptible = 0
        n_infected = 0
        n_immune = 0
        n_killed = 0

        for i in range(self.n):
            for j in range(self.n):
                # specify the neighborhood
                if self.grid[i, j].get_status() == 1 and self.grid[(i-1)%self.n, (j-1)%self.n].get_status() == 0:
                    neighbors.append(((i-1)%self.n, (j-1)%self.n))
                elif self.grid[i, j].get_status() == 1 and self.grid[(i-1)%self.n, j%self.n].get_status() == 0:
                    neighbors.append(((i-1)%self.n, j%self.n))
                elif self.grid[i, j].get_status() == 1 and self.grid[(i-1)%self.n, (j+1)%self.n].get_status() == 0:
                    neighbors.append(((i-1)%self.n, (j+1)%self.n))

                elif self.grid[i, j].get_status() == 1 and self.grid[i%self.n, (j-1)%self.n].get_status() == 0:
                    neighbors.append((i%self.n, (j-1)%self.n))
                elif self.grid[i, j].get_status() == 1 and self.grid[i%self.n, j%self.n].get_status() == 0:
                    neighbors.append((i%self.n, j%self.n))
                elif self.grid[i, j].get_status() == 1 and self.grid[i%self.n, (j+1)%self.n].get_status() == 0:
                    neighbors.append((i%self.n, (j+1)%self.n))

                elif self.grid[i, j].get_status() == 1 and self.grid[(i+1)%self.n, (j-1)%self.n].get_status() == 0:
                    neighbors.append(((i+1)%self.n, (j-1)%self.n))
                elif self.grid[i, j].get_status() == 1 and self.grid[(i+1)%self.n, j%self.n].get_status() == 0:
                    neighbors.append(((i+1)%self.n, j%self.n))
                elif self.grid[i, j].get_status() == 1 and self.grid[(i+1)%self.n, (j+1)%self.n].get_status() == 0:
                    neighbors.append(((i+1)%self.n, (j+1)%self.n))

        # for readability this is not concatenated with the upper for loop
        # it would be possible though
        for i in range(self.n):
            for j in range(self.n):
                # count the individual states
                if self.grid[i, j].status == 0:
                    n_susceptible += 1
                elif self.grid[i, j].status == 1:
                    n_infected += 1
                elif self.grid[i, j].status == 2:
                    n_immune += 1
                elif self.grid[i, j].status == 3:
                    n_killed += 1

        susceptible_list.append(n_susceptible)
        infected_list.append(n_infected)
        immune_list.append(n_immune)
        killed_list.append(n_killed)

        to_infect = draw_from_dataset(neighbors, 0.4)
        #to_infect = neighbors
        for i in to_infect:
            self.grid[i[0], i[1]].infect()
        return susceptible_list, infected_list, immune_list, killed_list, self.grid.astype(dtype=str).astype(dtype=int)


if __name__ == "__main__":
    colors = ["#3b528b", "#5ec962", "#fde725", "000000"]
    cmap = LinearSegmentedColormap.from_list("mycmap", colors)
    norm = plt.Normalize(0, 3)

    fig = plt.figure(figsize=(13, 5))
    subfigs = fig.subfigures(1, 2)
    ax_grid = subfigs[0].subplots()
    ax_graph = subfigs[1].subplots()

    grid = Grid(100)
    n_susceptible = []
    n_infected = []
    n_immune = []
    n_killed = []
    for i in tqdm(range(1000)):

        n_susceptible, n_infected, n_immune, n_killed, states = grid.update(n_susceptible, n_infected, n_immune, n_killed)
    ax_grid.imshow(states, cmap=cmap, norm=norm)
    ax_graph.plot(n_susceptible, color=colors[0])
    ax_graph.plot(n_infected, color=colors[1])
    ax_graph.plot(n_immune, color=colors[2])
    ax_graph.plot(n_killed, color=colors[3])
    plt.savefig("images/last.png")

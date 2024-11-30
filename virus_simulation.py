import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from tqdm import tqdm

def draw_from_dataset(dataset, prop):
    """
    :param dataset: the set of entries from which we choose
    :param prop: propability cutoff between 0 and 1
    :return: selected entries of the dataset
    """
    props = np.random.uniform(0, 1, len(dataset))
    mask = np.array(props <= 1-prop)
    index = range(len(dataset))
    compressed = np.ma.masked_array(index, mask).compressed()

    try:
        return np.array(dataset)[compressed]
    except IndexError:
        return []

class Virus(property):
    mean_contagious_period: int = 100
    sdev_contagious_period: int = 3
    mean_immune_period: int = 50
    sdev_immune_period: int = 10
    kill_prop: float = 0.0001
    infect_prop: float = 0.1

class Agent:
    def __init__(self, x, y):
        """
        :param x: the x coordinate of the agent on the grid
        :param y: the y coordinate of the agent on the grid
        """
        self.x = x
        self.y = y
        # as we implement the SIRD model, each agent is either susceptible, infected, recovered/immune or dead
        # hence the status 0, 1, 2 or 3
        self.status = 0
        # as contagiousness and immunity come in time periods, we need counters to keep track when an agent became contagious and or immune
        self.contagious_counter = 0
        self.immune_counter = 0

    def __repr__(self):
        # this only enables us to work with a readable representation of the object
        # in this case, the status is all we need
        return repr(self.status)

    def make_susceptible(self):
        self.contagious_counter = 0
        self.status = 0

    def infect(self):
        self.status = 1

    def immunize(self):
        self.status = 2

    def kill(self):
        self.status = 3

    # the get status function is called once per step so we can use it to count the number of time steps an agent is infected since the infect function was called
    def get_status(self):
        """
        :return self.status: which is the status of the agent
        """
        # as some agents experience the contagiousness and or the immunity longer or shorter, we pick the time periods from a normal distribution
        # the distributions are centered around the mean and spread with a standard deviation specified in the Virus property class
        self.contagious_period = np.random.normal(loc=Virus.mean_contagious_period, scale=Virus.sdev_contagious_period)
        self.immune_period = np.random.normal(loc=Virus.mean_immune_period, scale=Virus.sdev_immune_period)

        # here we increase the contagious counter by 1 each time the get_status function is called if the agent is infected and if the agent is still in the contagious period
        if self.status == 1 and self.contagious_counter < self.contagious_period:
            self.contagious_counter += 1
            # if the contagious counter exceeds the contagious period, draw a sample between 0 and 1 from a uniform distribution and depending on the kill propability, kill the agent or immunize the agent
            # after either one of both events, reset the contagious counter
            if self.contagious_counter >= self.contagious_period:
                sample = np.random.uniform(0, 1)
                if 1-Virus.kill_prop <= sample:
                    self.kill()
                else:
                    self.immunize()
                self.contagious_counter = 0

        # here we increase the immune counter by 1 each time the get_status function is called if the agent is immune and if the agent is still in the immune period
        elif self.status == 2 and self.immune_counter < self.immune_period:
            self.immune_counter += 1
            # if the immune counter exceeds the immune period, make the agent susceptible again and reset the immune counter
            if self.immune_counter >= self.immune_period:
                self.make_susceptible()
                self.immune_counter = 0
        return self.status


class Grid:
    def __init__(self, n):
        """
        :param n: specify the side length of the quadratic grid
        """

        self.n = n
        self.grid = np.empty((n,n), object)

        # initialize the grid by infecting the agent at (0, 0) and by making the rest susceptible to the disease
        for i in range(self.n):
            for j in range(self.n):
                agent = Agent(i, j)
                # specify initial configuration
                if (i, j) == (0, 0):
                    agent.infect()
                else:
                    agent.make_susceptible()
                self.grid[i, j] = agent

        # the agent class has a __repr__ dunder method which returns the self.status instance variable
        # uncomment the print to get a matrix representation of the grid
        #print(self.grid)


    def update(self, susceptible_list, infected_list, immune_list, killed_list):
        """
        :param susceptible_list: is an empty list in which the cumulative sum of susceptible agents will be stored
        :param infected_list: is an empty list in which the cumulative sum of infected agents will be stored
        :param immune_list: is an empty list in which the cumulative sum of immune agents will be stored
        :param killed_list: is an empty list in which the cumulative sum of killed agents will be stored
        :return: the filled lists as well as a matrix representation of the grid
        """
        neighbors = []
        n_susceptible = 0
        n_infected = 0
        n_immune = 0
        n_killed = 0

        # here we specify the neighborhood, which essentially is a 3x3 ring around the ith agent
        # we carefully check if a neighboring agent is already infected
        # the modulus % is important for indexing as well as to ensure periodic boundaries
        for i in range(self.n):
            for j in range(self.n):
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

        to_infect = draw_from_dataset(neighbors, Virus.infect_prop)
        # infect the selected agents
        for i in to_infect:
            self.grid[i[0], i[1]].infect()

        return susceptible_list, infected_list, immune_list, killed_list, self.grid.astype(dtype=str).astype(dtype=int)


if __name__ == "__main__":

    # specify the discrete colormap for the four states
    colors = ["#3b528b", "#5ec962", "#fde725", "000000"]
    cmap = LinearSegmentedColormap.from_list("mycmap", colors)
    norm = plt.Normalize(0, 3)

    # specify the figure and the subfigures (grid and graph)
    fig = plt.figure(figsize=(13, 5))
    subfigs = fig.subfigures(1, 2)
    ax_grid = subfigs[0].subplots()
    ax_graph = subfigs[1].subplots()

    # make an instance of the grid object and specify the length n of the square grid
    grid = Grid(n=200)

    # make empty lists to store the statistics
    n_susceptible = []
    n_infected = []
    n_immune = []
    n_killed = []

    # in the range function specify the number of time steps after the simulation terminates
    for i in tqdm(range(100)):
        n_susceptible, n_infected, n_immune, n_killed, states = grid.update(n_susceptible, n_infected, n_immune, n_killed)

    # indent in the following lines and set the argument in the savefig function to "images/{}.png".format(i) to store the individual time steps
    ax_grid.imshow(states, cmap=cmap, norm=norm)
    ax_graph.plot(n_susceptible, color=colors[0])
    ax_graph.plot(n_infected, color=colors[1])
    ax_graph.plot(n_immune, color=colors[2])
    ax_graph.plot(n_killed, color=colors[3])
    plt.savefig("last_step.png")

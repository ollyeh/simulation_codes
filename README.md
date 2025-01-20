# Simulation codes
Simulation codes is a collection of very simple python programs which model problems from statistical physics. The ambition of this collection is to break down the microscopic laws that govern phenomena like pressure or diffusion. Most importantly, the codes should help in understanding how these microscopic laws are implemented, making heavy use of Jupyter notebooks and excessively commented code.


## ideal_gas.ipynb
Make sure you have Jupyter Notebook or VSCode installed, depending on your personal preference. I decided to use the ArtistAnimation class from matplotlib, which exports the simulation as a mp4 video. Therefore, make sure you have ffmpeg installed as well. In the Notebook you get a step by step walkthrough of my thoughts, when I implemented the time evolution, the elastic collisions and the impulse histogram. Over time new functions will be implemented following the same step by step fashion! Note that explainer sections will be added as soon as I have more time. :)

![Early step of the simulation](examples/ideal_gas_beginning.jpg)

## virus_simulation.py
Make sure you have numpy, matplotlib and tqdm installed. In the Virus property class you can specify the virus' behaviour. Colors of the individual agents can be specified in the if \_\_name\_\_ == "\_\_main\_\_" codeblock in line 190. Here in order to obtain a discrete colormap of 4 colors for all four possible, the argument range ranges from 0 to 3. Currently, blue agents are susceptible to the virus, green agents are infected, yellow agents have recovered and black agents are dead. Please feel free to add a legend and add titles to the axes if needed. :)
The number of agents per side can be specified in line 201. This of course corresponds to the side length of the square in units of agents.
When running the code, only the last system configuration is saved to file. To save every time step, make sure to indent lines 214 to 219 and to change the argument in the savefig function to "images/{}.png".format(i). Of course here it is necessary to create an images folder in the program's directory.

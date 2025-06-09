import random
import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial.distance import pdist, squareform

def plot_tsp(nodes, route):
    """
    Plot the TSP nodes and route.

    Parameters:
    - nodes: List of tuples containing the coordinates of each node.
    - route: List of node indices representing the TSP route.
    """
    x = [node[0] for node in nodes]
    y = [node[1] for node in nodes]

    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, color='blue', zorder=2)  # Plot nodes


    for i in range(len(route) - 1):
        node1 = route[i]
        node2 = route[i + 1]
        plt.plot([nodes[node1][0], nodes[node2][0]], [nodes[node1][1], nodes[node2][1]], color='red', zorder=1)  # Plot route

    # Connect the last node to the first node to form a loop
    node1 = route[-1]
    node2 = route[0]
    #plt.plot([nodes[node1][0], nodes[node2][0]], [nodes[node1][1], nodes[node2][1]], color='red', zorder=1)  # Plot route

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('TSP Nodes and Route')
    plt.grid(True)
    plt.show()


def create_initial_population(pop_size,num_cities):
    population = []
    for i in range(pop_size):
    # crear solucion
        individual= list(np.random.permutation(num_cities))
        population.append(individual)
    return population

#print(create_initial_population(10,5))

def fitness(solution): # depende del problema
  distance = 0
  for i in range(len(solution)-1):
    distance += distances[solution[i]][solution[i+1]]
  return distance



N = 5 # num cities
pop_size = 8 # population size
cities = np.random.rand(N, 2)
distances = squareform(pdist(cities, 'euclidean'))
#print(positions)
#print(distances)

population = create_initial_population(pop_size,N)

#print(population)
#plot_tsp(cities,population[0])
#plot_tsp(cities,population[1])
#plot_tsp(cities,population[2])

def roulette_wheel_selection_minimization(population,all_fitness):
    max_fitness = max(all_fitness)
    inverted_fitness=[max_fitness-f for f in all_fitness]
    total_fitness=sum(inverted_fitness)
    selection_probs=[fitness/total_fitness for fitness in inverted_fitness]
    return population[np.random.choice(len(population),p=selection_probs)]

"""all_fitness=[fitness(sol) for sol in population]
selected=roulette_wheel_selection(population,all_fitness)
print("Size:",len(population))
print("N:", N)
print("Population Size:", population)
print("Fitness:", all_fitness)
print("Selected:",selected)"""

def single_point_crossover(parent1,parent2):
    cross_over_point=random.randint(1,len(parent1)-1)
    offspring1=parent1[:cross_over_point]+parent2[cross_over_point:]
    offspring2=parent2[:cross_over_point]+parent1[cross_over_point:]
    return offspring1,offspring2

"""h1,h2=single_point_crossover(population[0],population[1])

print("Parents:",population[0],population[1])
print('Offspring:',h1,h2)"""

def fill_child(child, parent, end):
    size = len(parent)
    current_pos = (end + 1) % size
    for gene in parent:
        if gene not in child:
            child[current_pos] = gene
            current_pos = (current_pos + 1) % size

def ordered_crossover(parent1,parent2):
    size=len(parent1)
    child1=[-1]*size
    child2=[-1]*size

    start, end = sorted(random.sample(range(size), 2))
    child1[start:end+1] = parent2[start:end+1]
    child2[start:end+1] = parent1[start:end+1]

    fill_child(child1, parent1, end)
    fill_child(child2, parent2, end)

    return child1, child2

"""offspring1, offspring2 = ordered_crossover(population[0], population[1])
print("Parents:", population[0], population[1])
print("Offspring:", offspring1, offspring2)"""


def swap_mutate(individual):
  i, j = np.random.choice(len(individual), 2, replace=False) # two random indices
  new_individual = individual.copy()
  new_individual[i], new_individual[j] = individual[j], individual[i]
  return new_individual

"""mutated = swap_mutate(population[0])
print("Original: \t", population[0])
print("Mutated: \t", mutated)"""

def select_elite(population, all_fitness, elite_size):   # selecciona los que tengan el menor fitness
  elite_indices = np.argsort(all_fitness)[:elite_size]
  return np.array(population)[elite_indices], elite_indices


all_fitness = [ fitness(sol) for sol in population]
selected_elite, indices = select_elite(population, all_fitness, 2)

"""print("Population:", population)
print("Fitness:", all_fitness)
print("Selected Elite:", selected_elite)
print("Selected indices:", indices)

# para imprimir con mejor vista
import pandas as pd
data = {'Population': population, 'Fitness': all_fitness}
df = pd.DataFrame(data)
print(df)"""


history = []

# Genetic Algorithm
def genetic_algorithm(distance_matrix, mutation_rate, generations):
    num_cities = distance_matrix.shape[0]
    population = create_initial_population(pop_size, N) # population size and num cities
    all_fitness = [ fitness(sol) for sol in population]

    for generation in range(generations):
        new_population = []

        # Preserve elite individuals
        selected_elite, elite_indices = select_elite(population, all_fitness, elite_size)
        new_population.extend(selected_elite)

        # Create new population through crossover and mutation
        while len(new_population) < pop_size:
            parent1 = roulette_wheel_selection_minimization(population, all_fitness)
            parent2 = roulette_wheel_selection_minimization(population, all_fitness)
            child1, child2 = ordered_crossover(parent1, parent2)

            if random.random() < mutation_rate:
                child1 = swap_mutate(child1)
            if random.random() < mutation_rate:
                child2 = swap_mutate(child2)

            new_population.extend([child1, child2])

        population = new_population[:pop_size] # replace with new population
        all_fitness = [ fitness(sol) for sol in population]
        if generation % 50 == 0:
          print(f"Generation {generation} | Best distance: {min(all_fitness)}")
          history.append([generation, min(all_fitness)])


    best_route_index = np.argmin(all_fitness)
    best_route = population[best_route_index]
    best_distance = all_fitness[best_route_index]

    print(f"Final best distance: {best_distance}")
    return best_route, best_distance

# hyperparametros
"""pop_size = 100
N = 50
elite_size = 10
mutation_rate = 0.01
generations = 5000"""

pop_size = 200
N = 100
elite_size = 50
mutation_rate = 0.05
generations = 5000

cities = np.random.rand(N, 2)
distances = squareform(pdist(cities, 'euclidean'))

best_route, best_distance = genetic_algorithm(distances, mutation_rate, generations)
plot_tsp(cities, best_route)
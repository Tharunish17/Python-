# vanet_simulation.py
# A complete Python simulation of VANET routing using Ant Colony Optimization.
# This script simulates and compares Standard ACO and Dynamic Pheromone Evaporation (DPE) ACO.

import numpy as np
import matplotlib.pyplot as plt

# --- Simulation Parameters ---
# --- CHOOSE THE ALGORITHM ---
USE_DPE_ACO = True  # Set to True for DPE-ACO (Zhao & Chen, 2025), False for Standard ACO (Li & Khan, 2024)

# City Grid Parameters
GRID_SIZE = 10
NUM_NODES = GRID_SIZE * GRID_SIZE

# Vehicle Parameters
NUM_VEHICLES = 50

# ACO Parameters
NUM_ANTS = 40         # Number of ants per pathfinding mission
ALPHA = 1.0           # Pheromone influence factor
BETA = 2.0            # Heuristic (distance) influence factor
RHO = 0.1             # Base pheromone evaporation rate
Q = 100.0             # Pheromone deposit constant

# DPE-ACO Specific Parameter (Zhao & Chen, 2025)
K_CONGESTION = 0.5    # Sensitivity to congestion for dynamic evaporation

# Simulation Time
MAX_TIME_STEPS = 100

def create_city_grid(grid_size):
    """
    Creates a grid-based city map.
    Returns:
        adj_matrix (ndarray): Adjacency matrix where adj[i, j] = 1 if connected.
        node_coords (ndarray): An (N, 2) array of [x, y] coordinates for each node.
    """
    num_nodes = grid_size ** 2
    adj_matrix = np.zeros((num_nodes, num_nodes))
    node_coords = np.zeros((num_nodes, 2))
    
    for r in range(grid_size):
        for c in range(grid_size):
            node_id = r * grid_size + c
            node_coords[node_id] = [c, r]
            # Connect to the right neighbor
            if c < grid_size - 1:
                neighbor_id = node_id + 1
                adj_matrix[node_id, neighbor_id] = 1
                adj_matrix[neighbor_id, node_id] = 1
            # Connect to the neighbor below
            if r < grid_size - 1:
                neighbor_id = node_id + grid_size
                adj_matrix[node_id, neighbor_id] = 1
                adj_matrix[neighbor_id, node_id] = 1
    return adj_matrix, node_coords

def initialize_vehicles(num_vehicles, num_nodes):
    """Initializes vehicle agents with random start and end points."""
    vehicles = []
    for _ in range(num_vehicles):
        start_node, end_node = np.random.choice(num_nodes, 2, replace=False)
        vehicles.append({
            'start_node': start_node,
            'end_node': end_node,
            'current_node': start_node,
            'path': [],
            'path_index': 0,
        })
    return vehicles

def find_path_aco(start_node, end_node, num_ants, pheromone, heuristic, adj, alpha, beta):
    """Finds the best path from start to end using the ACO algorithm."""
    all_paths = []
    for _ in range(num_ants):
        path = [start_node]
        current_node = start_node
        while current_node != end_node and len(path) < adj.shape[0]:
            neighbors = np.where(adj[current_node] > 0)[0]
            # Exclude nodes already in the path to avoid loops
            valid_neighbors = [n for n in neighbors if n not in path]
            
            if not valid_neighbors:
                break # Ant is stuck
            
            # Calculate selection probabilities
            ph_vals = pheromone[current_node, valid_neighbors] ** alpha
            he_vals = heuristic[current_node, valid_neighbors] ** beta
            
            probs = ph_vals * he_vals
            if np.sum(probs) == 0: # If all probabilities are zero, choose randomly
                probs = np.ones(len(valid_neighbors))
            
            probs /= np.sum(probs)
            
            next_node = np.random.choice(valid_neighbors, p=probs)
            path.append(next_node)
            current_node = next_node
        
        if path[-1] == end_node:
            all_paths.append(path)
            
    if not all_paths:
        return [] # No path found
        
    # Return the shortest path found by the ants
    best_path = min(all_paths, key=len)
    return best_path

def move_vehicles(vehicles, adj_matrix):
    """Moves vehicles one step and calculates node congestion."""
    congestion = np.zeros(adj_matrix.shape[0])
    completed_trips_this_step = []

    for v in vehicles:
        if v['path']:
            v['path_index'] += 1
            if v['path_index'] >= len(v['path']):
                # Vehicle reached destination, reset for a new trip
                completed_trips_this_step.append(len(v['path']) - 1)
                new_start = v['end_node']
                new_end = np.random.randint(adj_matrix.shape[0])
                while new_start == new_end:
                    new_end = np.random.randint(adj_matrix.shape[0])
                
                v['start_node'] = new_start
                v['end_node'] = new_end
                v['current_node'] = new_start
                v['path'] = []
                v['path_index'] = 0
            else:
                v['current_node'] = v['path'][v['path_index']]
        
        congestion[v['current_node']] += 1
    return vehicles, congestion, completed_trips_this_step

def update_pheromones(pheromone, paths, Q, rho, use_dpe, congestion, k_cong):
    """Updates pheromone matrix with evaporation and new deposits."""
    # Evaporation
    if use_dpe:
        # Dynamic Evaporation (Zhao & Chen, 2025)
        max_cong = np.max(congestion)
        if max_cong == 0: max_cong = 1 # Avoid division by zero
        # Reshape congestion to allow broadcasting
        congestion_col = congestion[:, np.newaxis]
        congestion_row = congestion[np.newaxis, :]
        node_congestion_matrix = (congestion_col + congestion_row) / 2
        
        dynamic_rho = rho + k_cong * (node_congestion_matrix / max_cong)
        pheromone *= (1 - dynamic_rho)
    else:
        # Standard Evaporation (Li & Khan, 2024)
        pheromone *= (1 - rho)

    # Deposition
    for path in paths:
        if path:
            path_len = len(path) - 1
            deposit_amount = Q / path_len
            for i in range(path_len):
                node1, node2 = path[i], path[i+1]
                pheromone[node1, node2] += deposit_amount
                pheromone[node2, node1] += deposit_amount # Symmetric update
    return pheromone

def visualize_state(coords, adj, vehicles, pheromone, title_str):
    """Plots the current state of the simulation."""
    plt.clf()
    ax = plt.gca()
    
    # Plot roads with pheromone levels
    max_ph = np.max(pheromone[adj > 0]) if np.any(pheromone[adj > 0]) else 1.0
    for i in range(adj.shape[0]):
        for j in range(i + 1, adj.shape[0]):
            if adj[i, j] > 0:
                p_level = pheromone[i, j] / max_ph
                color = (0.8 * (1 - p_level), 0.8 * (1 - p_level) + 0.5 * p_level, 0.8 * (1 - p_level))
                line_width = 0.5 + p_level * 4
                ax.plot([coords[i, 0], coords[j, 0]], [coords[i, 1], coords[j, 1]], 
                        color=color, linewidth=line_width, zorder=1)

    # Plot nodes
    ax.plot(coords[:, 0], coords[:, 1], 'ks', markersize=8, zorder=2)
    
    # Plot vehicles
    vehicle_pos = np.array([coords[v['current_node']] for v in vehicles])
    ax.plot(vehicle_pos[:, 0], vehicle_pos[:, 1], 'bo', markersize=6, zorder=3, label='Vehicles')
    
    plt.title(title_str)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.pause(0.01)

def main():
    """Main simulation function."""
    print("Initializing simulation...")
    
    # Setup
    adj_matrix, node_coords = create_city_grid(GRID_SIZE)
    heuristic_info = 1 / (adj_matrix + np.finfo(float).eps) # Inverse of distance
    pheromone_matrix = np.ones((NUM_NODES, NUM_NODES)) * 0.1
    vehicles = initialize_vehicles(NUM_VEHICLES, NUM_NODES)
    
    avg_trip_times = []
    total_completed_trips = 0

    plt.ion()
    fig = plt.figure(figsize=(8, 8))
    
    # Main Loop
    for t in range(MAX_TIME_STEPS):
        algo_name = "DPE-ACO (Zhao & Chen, 2025)" if USE_DPE_ACO else "Standard ACO (Li & Khan, 2024)"
        title_str = f'{algo_name} | Time: {t+1}/{MAX_TIME_STEPS}'
        print(title_str)
        
        # 1. Pathfinding for vehicles that need a path
        paths_this_step = []
        for v in vehicles:
            if not v['path']:
                path = find_path_aco(v['start_node'], v['end_node'], NUM_ANTS, pheromone_matrix,
                                     heuristic_info, adj_matrix, ALPHA, BETA)
                v['path'] = path
                paths_this_step.append(path)

        # 2. Move vehicles and calculate congestion
        vehicles, congestion, completed_trips = move_vehicles(vehicles, adj_matrix)
        if completed_trips:
            avg_trip_times.append(np.mean(completed_trips))
            total_completed_trips += len(completed_trips)
        
        # 3. Update pheromones
        pheromone_matrix = update_pheromones(pheromone_matrix, paths_this_step, Q, RHO,
                                            USE_DPE_ACO, congestion, K_CONGESTION)

        # 4. Visualize
        visualize_state(node_coords, adj_matrix, vehicles, pheromone_matrix, title_str)

    plt.ioff()
    
    # Final Performance Plot
    plt.figure(figsize=(10, 5))
    plt.plot(avg_trip_times, '-o', label='Average Trip Time')
    plt.xlabel('Batch of Completed Trips')
    plt.ylabel('Average Trip Duration (Time Steps)')
    plt.title(f'Performance Analysis: {algo_name}\nTotal Completed Trips: {total_completed_trips}')
    plt.grid(True)
    plt.legend()
    plt.show()

    print("Simulation finished.")

if __name__ == "__main__":
    main()
from flask import Flask, render_template, jsonify, request
import json
import math
import random
import numpy as np
from typing import List, Dict, Any
import time

app = Flask(__name__)

class EquationGene:
    """Represents a single equation variant with its parameters"""
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.fitness = 0.0
        self.id = 0
        self.mutation_log: List[str] = []
    
    def mutate(self, mutation_rate: float = 0.3, category_weights: Dict[str, float] | None = None, penalties: Dict[str, float] | None = None):
        """Apply mutations to the equation parameters - only trigonometric functions now"""
        trig_functions = ['sin', 'cos', 'tan', 'atan']
        # Only mutate trigonometric functions - numeric parameters controlled by sliders
        trig_keys = {k for k in self.params.keys() if k.startswith('trig')}

        if category_weights is None:
            category_weights = {'trig': 1.0}  # Only trig mutations
        if penalties is None:
            penalties = {}

        # Build weighted choice list with penalties
        weighted = []
        for cat, w in category_weights.items():
            penalty = penalties.get(cat, 1.0)
            adjusted_weight = w * penalty
            weighted += [cat] * max(1, int(adjusted_weight * 100))

        self.mutation_log = []
        for key, value in list(self.params.items()):
            if random.random() < mutation_rate:
                category = random.choice(weighted)
                if category == 'trig' and key in trig_keys and isinstance(value, str):
                    newv = random.choice(trig_functions)
                    if newv != value:
                        self.params[key] = newv
                        self.mutation_log.append(f"{key}:{value}->{newv}")

class GeneticEquationEvolver:
    def __init__(self, population_size: int = 3, elite_size: int = 1):
        self.population_size = population_size
        self.elite_size = elite_size
        self.generation = 0
        self.population: List[EquationGene] = []
        self.feedback_history = []
        self.elites: List[EquationGene] = []
        self.next_node_id = 1
        self.graph: Dict[str, Any] = {'nodes': [], 'edges': [], 'feedback': []}
        self.mutation_penalties: Dict[str, float] = {}  # Track penalized mutations
        
        # Base equation parameters derived from yiyi.html
        self.base_params = {
            'k_div': 4,
            'k_sub': 12.5,
            'e_div': 9,
            'e_add': 9,
            'o_div': 9,
            'x_offset': 60,
            'y_trig_div': 8,
            'q_mult': 0.7,
            'px_add': 200,
            'py_add': 200,
            'py_q_div': 3,
            'time_mult': 1/12,
            # trig sites
            'trig_y': 'cos',      # cos(y)
            'trig_e': 'sin',      # sin(e)
            'trig_o': 'sin',      # sin(o*4 - t)
            'trig_c_sin': 'sin',  # sin(c)
            'trig_c_cos': 'cos',  # cos(c - 1)
            'trig_c4_cos': 'cos'  # cos(c*4 - o)
        }
        
        self.initialize_population()
    
    def initialize_population(self):
        """Create initial population with base equation + mutations"""
        for i in range(self.population_size):
            params = self.base_params.copy()
            gene = EquationGene(params)
            gene.id = i + 1
            gene.global_id = self.next_node_id; self.next_node_id += 1
            gene.mutate(mutation_rate=0.4, category_weights=self.current_category_weights(), penalties=self.mutation_penalties)
            self.log_node(gene, parent_id=0)
            self.population.append(gene)
        # Seed elites with the first few variants (will be replaced after first feedback)
        self.elites = [g for g in self.population[:self.elite_size]]
    
    def evaluate_population(self, feedback_ids: List[int]):
        """Update fitness based on user feedback"""
        for gene in self.population:
            gene.fitness = 0.0
        
        for gene_id in feedback_ids:
            if 1 <= gene_id <= len(self.population):
                self.population[gene_id - 1].fitness = 1.0
        
        self.population.sort(key=lambda x: x.fitness, reverse=True)
    
    def evolve_generation(self, feedback_ids: List[int]):
        """Evolve to next generation based on feedback"""
        # Keep reference to current generation before replacing
        prev_population = list(self.population)
        self.evaluate_population(feedback_ids)
        
        self.feedback_history.append({
            'generation': self.generation,
            'selected_ids': feedback_ids,
            'elite_params': [gene.params for gene in self.population[:self.elite_size]]
        })
        
        # Handle "none selected" case - penalize current mutations and go back to previous elite
        if not feedback_ids:
            self.penalize_current_mutations()
            # Go back to previous generation's elite and mutate again
            if self.generation > 0:
                # Use previous generation's elite as base
                prev_elite = self.elites if self.elites else [EquationGene(self.base_params.copy())]
            else:
                prev_elite = [EquationGene(self.base_params.copy())]
        else:
            # Refresh elites (kept internally, not shown directly)
            self.elites = [self.population[i] for i in range(self.elite_size)]
            prev_elite = self.elites

        # Log feedback mapping to global ids
        selected_global = []
        for x in feedback_ids:
            if 1 <= x <= len(prev_population):
                selected_global.append(getattr(prev_population[x-1], 'global_id', None))
        self.graph['feedback'].append({'generation': self.generation, 'selected': selected_global})

        # Generate a FULL set of mutated children to display as choices
        new_population: List[EquationGene] = []
        weights = self.current_category_weights()
        for i in range(self.population_size):
            parent = random.choice(prev_elite)
            child = EquationGene(parent.params.copy())
            child.id = i + 1
            child.mutate(mutation_rate=0.25, category_weights=weights, penalties=self.mutation_penalties)
            # Ensure at least one visible mutation
            if not child.mutation_log:
                self.force_single_mutation(child, weights)
            child.global_id = self.next_node_id; self.next_node_id += 1
            # Log node and edge
            self.log_node(child, parent_id=getattr(parent, 'global_id', 0))
            self.graph['edges'].append({'from': getattr(parent, 'global_id', 0), 'to': child.global_id, 'gen': self.generation})
            new_population.append(child)

        self.population = new_population
        self.generation += 1
        self.save_graph()
    
    def current_category_weights(self) -> Dict[str, float]:
        """Return mutation category weights - only trigonometric functions now."""
        # All generations focus on trigonometric function exploration
        return {'trig': 1.0}

    def force_single_mutation(self, gene: EquationGene, weights: Dict[str, float]):
        """Guarantee at least one mutation is recorded for a child - only trigonometric functions."""
        # Only mutate trigonometric functions
        trig_sites = [k for k in gene.params.keys() if k.startswith('trig')]
        if trig_sites:
            site = random.choice(trig_sites)
            funcs = ['sin', 'cos', 'tan', 'atan']
            newf = random.choice(funcs)
            oldf = gene.params[site]
            if newf == oldf:
                newf = random.choice([f for f in funcs if f != oldf])
            gene.params[site] = newf
            gene.mutation_log.append(f"{site}:{oldf}->{newf}")

    def log_node(self, gene: EquationGene, parent_id: int):
        self.graph['nodes'].append({
            'id': getattr(gene, 'global_id', None),
            'gen': self.generation,
            'parent': parent_id,
            'params': gene.params,
            'mutations': gene.mutation_log
        })

    def penalize_current_mutations(self):
        """Penalize mutations from current generation by 30% - only trigonometric functions now"""
        for gene in self.population:
            for mutation in gene.mutation_log:
                # Extract category from mutation string
                if '->' in mutation:
                    key = mutation.split(':')[0]
                    if key.startswith('trig'):
                        cat = 'trig'
                        # Apply 30% penalty
                        current_penalty = self.mutation_penalties.get(cat, 1.0)
                        self.mutation_penalties[cat] = current_penalty * 0.7

    def save_graph(self):
        try:
            with open('exploration_log.json', 'w', encoding='utf-8') as f:
                json.dump(self.graph, f, indent=2)
        except Exception:
            pass
    
    def get_population_data(self):
        """Get current population data for frontend"""
        return {
            'generation': self.generation,
            'variants': [
                {
                    'id': gene.id,
                    'params': gene.params,
                    'mutations': gene.mutation_log[:3]  # Show top 3 mutations
                }
                for gene in self.population
            ]
        }

# Global evolver instance
evolver = GeneticEquationEvolver()

@app.route('/')
def index():
    return render_template('genetic_evolver.html')

@app.route('/api/population')
def get_population():
    return jsonify(evolver.get_population_data())

@app.route('/api/evolve', methods=['POST'])
def evolve():
    data = request.get_json()
    feedback_ids = data.get('selected_ids', [])
    # Always evolve: empty selection means "Select None" feedback
    evolver.evolve_generation(feedback_ids)
    return jsonify({'success': True, 'generation': evolver.generation})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

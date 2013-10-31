'''
Use to represent a network of machines, then create a subset of those machines
Subset is based upon proximity and availability

Example usage:
network = Network(machine_test_data)
network.create_subset(target=50)
network.output_results()

Currently accepts test data from within document as input
Could easily be expanded to accept data from a wide variety of sources

__author__ = daniel.dearing
__date__ = 28.10.12

'''

import sys
import unittest
import random
import time

#itertools.combination is not included in libraries before v2.6
required_version = (2,6)
current_version = sys.version_info
if current_version >= required_version:
    from itertools import combinations
else:
    def combinations(iterable, r):
        # combinations('ABCD', 2) --> AB AC AD BC BD CD
        # combinations(range(4), 3) --> 012 013 023 123
        pool = tuple(iterable)
        n = len(pool)
        if r > n:
            return
        indices = range(r)
        yield tuple(pool[i] for i in indices)
        while True:
            for i in reversed(range(r)):
                if indices[i] != i + n - r:
                    break
            else:
                return
            indices[i] += 1
            for j in range(i+1, r):
                indices[j] = indices[j-1] + 1
            yield tuple(pool[i] for i in indices)




machine_test_data = {'CMP000001': {'location': 1, 'loaded_factor': 4},
                     'CMP000002': {'location': 2, 'loaded_factor': 8},
                     'CMP000003': {'location': 3, 'loaded_factor': 9},
                     'CMP000004': {'location': 2, 'loaded_factor': 9},
                     'CMP000005': {'location': 2, 'loaded_factor': 7},
                     'CMP000006': {'location': 4, 'loaded_factor': 8},
                     'CMP000007': {'location': 5, 'loaded_factor': 7},
                     'CMP000008': {'location': 3, 'loaded_factor': 6},
                     'CMP000009': {'location': 7, 'loaded_factor': 6},
                     'CMP000010': {'location': 9, 'loaded_factor': 4},
                     'CMP000011': {'location': 0, 'loaded_factor': 10},
                     'CMP000012': {'location': 6, 'loaded_factor': 9},
                     'CMP000013': {'location': 6, 'loaded_factor': 0},
                     'CMP000014': {'location': 7, 'loaded_factor': 1}}


location_map = {0: "New York", 1: "London", 2: "Zug", 3: "Amsterdam", 
                4: "Sydney", 5: "Berlin", 6: "Bejing", 7: "Tokyo", 
                8: "Paris", 9: "Chicago"}

dist_matrix = {0: [0, 5576.36, 6338.79, 5869.00, 16006.81, 6392.14, 11001.25,
                   10860.81, 5843.68, 1145.54],
               1: [5576.36, 0, 790.00, 357.76, 17012.72, 932.68, 8150.20,
                   9569.43, 343.93, 6360.10],
               2: [6338.79, 790.00, 0, 633.99, 16592.82, 690.50, 8006.55,
                   9607.88, 495.37, 7145.29],
               3: [5869.00, 357.76, 633.99, 0, 16661.72, 577.39, 7831.14, 
                   9298.85, 430.34, 6615.26],
               4: [16006.81, 17012.72, 16592.82, 16661.72, 0, 16112.23, 
                   8957.97, 7835.20, 16979.24, 14892.66],
               5: [6392.14, 932.68, 690.50, 577.39, 16112.23, 0, 7365.81, 
                   8926.12, 878.48, 7091.49],
               6: [11001.25, 8150.20, 8006.55, 7831.14, 8957.97, 7365.81, 0,
                   2094.73, 2094.73, 10615.38],
               7: [10860.81, 9569.43, 9607.88, 9298.85, 7835.20, 8926.12, 
                   2094.73, 0, 9722.95, 10149.48],
               8: [5843.68, 343.93, 495.37, 430.34, 16979.24, 878.48, 2094.73, 
                   9722.95, 0, 6658.08],
               9: [1145.54, 6360.10, 7145.29, 6615.26, 14892.66, 7091.49, 
                   10615.38, 10149.48, 6658.08, 0]}

class Machine(object):
    '''
    A representation of one machine in the network.
    
    Unpacks dictionary of data and creates an attribute for each key in dict.
    For each key, sets the property to its correlating value in dict
    
    Arguments:
        id -- the id for the machine
    Keyword arguments:
        data -- optional dictionary to create new properties on object
    
    '''
    def __init__(self, id, data = {}):
        self.id = id
        self._unpack_dict(data)
        
    def _unpack_dict(self, data):
        for k, v in data.items():
            setattr(self, k, v)
            
            
class Network(object):
    '''
    A class that describes all the machines across a network
    
    To create subset, call Network.create_subset()
    
    '''
    
    def __init__(self, machine_dict):
        '''
        Creates individual machine objects eg Machine() from a dict of machines
    
        Creates empty subset of all machines
        
        Arguments:
            machine_dict -- Dict of all machines in network
                            {id: [location:0, loaded_factor], ...}
                            
        '''
        self.all_machines = []
        self._instance_machines(machine_dict)
        self.set_subset()
        self.set_max_dist()
         
    def _instance_machines(self, machine_dict):
        for id, data in machine_dict.items():
            mr = Machine(id, data)
            self.all_machines.append(mr)
            
    def set_subset(self, value = [], append = False):
        '''Set current subset, option to append to existing subset
        '''
        if append:
            self._subset.append(value)
        else:
            self._subset = value
    
    def get_subset(self):
        '''Return current subset list
        '''
        return self._subset
        
    def set_max_dist(self, value = 0):
        '''Set maximum distance(km) that this network subset will require.
        '''
        self._max_dist = value
        
    def get_max_dist(self):
        '''Get maximum distance(km) that this network subset will require.
        '''
        return self._max_dist

    def create_subset(self, target=50):
        '''
        Creates subset of self.all_machines
        Should be used as the entry point for creating a network subset
        Returns a list of machines objects, class instances of Machine()
        
        Keyword arguments:
            target -- The amount of machines to make up subset
        
        '''
        #create empty list for possible subsets
        filtered = self._filter_machines('loaded_factor', 10)
        sorted_machines = self._sort_machines('location', filtered)
        numbers = [[dc, len(record)] for dc, record in sorted_machines.items()]
        self._subset_sum_recursive(numbers, target, list())
        if not self.get_subset():
            msg = 'Sorry not enough available machines '
            msg += 'for a subset of size %s. ' %(target)
            msg += 'Please lower target subset size'
            raise InputError(msg)
        self._subset_dist()
        sp = self._smallest_proximity()
        subset = self._map_machines(sp[0], sorted_machines, target)
        self.set_subset(subset)
        self.set_max_dist(sp[1])
        return self.get_subset()
    
    def output_results(self, list_machines=True):
        '''Convenience function to display the results of subset creation
        '''
        subset = self.get_subset()
        dist = self.get_max_dist()
        #unique locations
        udc = []
        info = ''
        #for machine object in subset
        for m in subset:
            location = location_map[m.location]
            if location not in udc:
                udc.append(location)
            info += '  %s: loaded factor = %s, location: %s\n' %(m.id, 
                                                m.loaded_factor, location)
        
        msg = "\nThe max distance between locations for this "
        msg += "subset of machines was: %.2fkm\n" %(dist)
        
        msg += "The subset of machines came from "
        msg += "the following locations: %s\n" %(', '.join(udc))
        msg += 'Subset size is: %d\n\n' %(len(subset))
        if list_machines:
            msg += "Recommended subset of available machines:\n%s" %(info)        
        print msg 
    
    def _filter_machines(self, prpty, value):
        '''
        Filter out machines that have a specific property less than the 
            specified value.
        
        Arguments:
            prpty -- the property of machine object we are interested
                     no specificity in case property name changes
            value -- the value for this property to compare against
        '''
        return filter(lambda x: getattr(x, prpty) < value, 
                               self.all_machines)
    
    def _sort_machines(self, prpty, machines):
        '''
        Returns a dictionary with all machines sorted under a particular key
        
        eg {'location: [machine, machine, ...], ...}
        
        '''
        grouped = {}
        for machine in machines:
            #the key is the requested property of the record eg 'location'
            #store the whole record under this property
            k = getattr(machine, prpty)
            if k not in grouped.keys():
                grouped[k] = [machine]
            else:
                grouped[k].append(machine)
        return grouped
                
    def _subset_sum_recursive(self, numbers, target, partial):
        '''
        Recursively goes through all combinations of locations that can give
            the required number of machines (target)
            
        When target number of machines is reached, add to subset.
        
        Then moves on to next possible combination
        
        Arguments:
            numbers -- nested list eg [[[1, 1], [2, 1], [3, 3], ...]
                       each list describes a location and available machines
                       ie. [[location, amount], ....]
            target -- the total number of machines we are looking for
            partial -- is the sub total in the machine count
                       starts with empty list
        
        '''
        s = sum([i[1] for i in partial if i])
        if s >= target: 
            self.set_subset(partial, append=True)
            #condition already met, no need to go further down the tree
            return  
            
        for i in range(len(numbers)):
            n = numbers[i]
            remaining = numbers[i+1:]
            self._subset_sum_recursive(remaining, target, partial + [n]) 

    def _subset_dist(self):
        '''
        Determines all possible combinations of two for list of locations
        
        Then updates the subset to only include the combination
            that had the smallest value for its maximum distance between
            any two locations
        
        '''
        subset_update = []
        subset = self.get_subset()
        for x in subset:
            locations = [y[0] for y in x]
            cmb = combinations(locations, 2)
            max_dist = 0
            for c in cmb:
                dist = dist_matrix[c[0]][c[1]]
                if dist > max_dist:
                    max_dist = dist
            subset_update += [[x,max_dist]]
        self.set_subset(subset_update)
            
    def _smallest_proximity(self):
        '''
        Determines which combination of locations have a smaller proximity.
        i.e The largest distance between any two locations,
            will be the smallest of any other possible combination of 
            locations.
        Returns nested list 
        eg [[location, machines_available], max distance]
        
        '''
        smallest = None
        for i in self.get_subset():
            dist = i[-1]
            if smallest:
                if dist <= smallest[1]:
                    #Prioritise fewer locations
                    #This will presumably have a smaller proximity
                    if len(i[0]) < len(smallest[0]):
                        smallest = i
            else:
                smallest = i     
        return smallest
        
    def _map_machines(self, spc, machine_dict, target):
        '''
        From the combination of locations that had the smallest proximity
        Find the machines associated with those locations
        
        Return the amount of machines that is specified by spc
        
        Arguments:
            spc -- Smallest proximity combination
                   Nested list - [[locations, machines_available],...]
                   eg [[1, 1], [2, 1], [3, 1]]
            machine_dict -- a dictionary where all the machine objects are
                            mapped to their respective locations
                            {location: [machine objects]}
        
        Returns list of machine objects                          
        '''
        machines = []
        for c in spc:
            location = c[0]
            amount_of_machines = c[1]
            ml = machine_dict[location]
            for m in range(amount_of_machines):
                if len(machines) == target:
                    return machines
                
                machines.append(ml[m])
        return machines

class InputError(Exception):
    def __init__(self, msg):
        print msg

class TestSubsetNetwork(unittest.TestCase):
    
    machine_test_data = {'CMP000001': {'location': 1, 
                                       'loaded_factor': 4},
                        'CMP000002': {'location': 2, 
                                      'loaded_factor': 8},
                        'CMP000003': {'location': 3, 
                                      'loaded_factor': 9}}
    
    def test_max_dist(self):
       n = Network(self.machine_test_data)
       n.create_subset(target=3)
       self.assertEqual(n.get_max_dist(), 790.00)
       
    def test_filter_machines(self):
       c = Network(self.machine_test_data)
       filtered_machines = c._filter_machines('loaded_factor', 8)
       
       self.assertEqual(len(filtered_machines), 1)
       
    def test_subset_target(self):
        b = Network(self.machine_test_data)
        b.create_subset(target=3)
        self.assertEqual(len(b.get_subset()), 3)


def test_scalability(output_results = True,):
    scalable_test_data = {}
    for i in range(5000):
        uid = '%05d'%(i)
        load = random.randint(0,10)
        loc = random.randint(0, 9)
        scalable_test_data['CMP%s'%(uid)] = {'location':loc, 
                                             'loaded_factor': load}
    st = time.time()
    a = Network(scalable_test_data)
    a.create_subset(target = 500)
    if output_results:
        a.output_results()
    total_time = time.time() - st
    msg =  'Total time taken to test program ' 
    msg += 'on a larger scale was %s secs' %(total_time)
                    
#===============================================================================
# if __name__ == "__main__":
#    #run some tests
#    suite = unittest.TestLoader().loadTestsFromTestCase(TestSubsetNetwork)
#    unittest.TextTestRunner(verbosity=2).run(suite)
#    test_scalability()
#===============================================================================
    
    
    

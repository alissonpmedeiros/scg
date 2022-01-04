#!/user/bin/python3
from dataclasses import dataclass
from numpy import random


@dataclass
class MecResources:
    """ generates MEC GPU and CPU workloads """

    #lam: rate or known number of occurences
    gpu_lam: int    = 15
    cpu_lam: int    = 60
    number_mecs: int = 100

    def generate_cpu_resources(self):
        """generates cpu resources for MEC servers"""
        cpu_set = random.poisson(lam=self.cpu_lam, size=self.number_mecs)
        return cpu_set

    def include_zero_values(self, array):
        """ randomly set zero values for GPUs on MEC servers """
        array_len  = len(array)
        percentage = int(array_len / 3.33) #define 30% of the array with zero values
        for i in range(0, percentage):
            while True:
                random_index = random.randint(0,array_len)
                if array[random_index] != 0:
                    array[random_index] = 0
                    break

        
    def generate_gpu_resources(self):
        """generates gpu resources for MEC servers"""
        gpu_set = random.poisson(lam=self.gpu_lam, size=self.number_mecs)
        self.include_zero_values(gpu_set)
        return gpu_set
    


@dataclass
class MecWorkloads:
    """ generates cpu and gpu workloads for mec servers"""

    pass